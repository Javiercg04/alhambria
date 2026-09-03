from pathlib import Path
import re, sys, os
import statistics
import numpy as np

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)

from extraccion import extraer_texto, limpiar_texto_completo

from chunking import (
    trocear_recursiva,
    trocear_semantica,
    trocear_por_palabra,
    trocear_por_caracteres,
    trocear_por_sentencias,
)
import indexado

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
BASE        = Path(__file__).parent
CORPUS      = BASE / ".." / "corpus"          # ahora se evalúa el corpus entero
SALIDA_EVAL = BASE / "salida_eval"
SALIDA_EVAL.mkdir(exist_ok=True)

MIN_PALABRAS = 15              # bajo esto, un chunk se considera "huérfano"
N_MUESTRA    = 3               # nº de chunks de ejemplo a volcar por estrategia

# Parámetros de la configuración final, los mismos que usa indexar.py.
# Si se cambian aquí hay que cambiarlos allí, o la tabla describiría una
# configuración distinta de la que generó el índice.
PERCENTIL = 75
TAM_MAX   = 1300
TAM_MIN   = 250
SOLAPE    = 200

# Diferencia máxima admisible entre factores de solape. Por encima, las
# estrategias no cubren la misma cantidad de texto y no son comparables.
UMBRAL_SOLAPE = 0.35


class Codificador:
    """Adaptador sobre src/indexado.py.

    Se usa el mismo codificador que construye el índice (tokenizer.onnx más
    el modelo cuantizado) en lugar de cargar un SentenceTransformer aparte.
    Absorbe los argumentos de sentence-transformers que aquí no aplican: los
    vectores salen ya normalizados del propio grafo ONNX.
    """

    def encode(self, textos, **kwargs):
        return indexado.generar_embedding(list(textos))


def preparar_texto(ruta):
    return limpiar_texto_completo(extraer_texto(ruta))


ABREVIATURAS = {
    "sr", "sra", "dr", "dra", "d", "dña", "ud", "uds", "prof", "profa",
    "pag", "pags", "pág", "págs", "vol", "vols", "num", "núm", "art", "arts",
    "cap", "caps", "fig", "figs", "ms", "mss", "p", "pp", "ej", "etc",
    "aprox", "g", "h", "r", "s", "n", "trad", "ed", "eds", "coord", "coords",
    "vid", "cf", "op", "loc", "cit", "ibid", "cfr",
}


def _dividir_en_frases(texto):
    patron = re.compile(r'([.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«])')
    frases, pos = [], 0
    for m in patron.finditer(texto):
        fin_signo = m.end(1)
        antes = texto[:fin_signo - 1]
        match_palabra = re.search(r'(\w+)$', antes)
        palabra = match_palabra.group(1).lower() if match_palabra else ""
        es_abreviatura_o_inicial = bool(palabra) and (len(palabra) <= 1 or palabra in ABREVIATURAS)
        if es_abreviatura_o_inicial:
            continue
        frases.append(texto[pos:fin_signo].strip())
        pos = m.end()
    resto = texto[pos:].strip()
    if resto:
        frases.append(resto)
    return [f for f in frases if f]


# ─────────────────────────────────────────────────────────────────────────────
# MÉTRICAS INTRÍNSECAS (sin preguntas)
# ─────────────────────────────────────────────────────────────────────────────
_FIN_LIMPIO = ('.', '!', '?', '»', '"', '…')


def empieza_limpio(chunk):
    c = chunk.lstrip()
    return bool(c) and (c[0].isupper() or c[0] in ('¿', '¡', '«', '"'))


def termina_limpio(chunk):
    c = chunk.rstrip()
    return bool(c) and c[-1] in _FIN_LIMPIO


import random

MAX_CHUNKS_COHESION = 300
SEMILLA_MUESTREO = 42


def cohesiones_por_chunk(chunks, modelo, batch_size=64):
    n_total = len(chunks)
    if n_total > MAX_CHUNKS_COHESION:
        random.seed(SEMILLA_MUESTREO)
        indices_evaluados = sorted(random.sample(range(n_total), MAX_CHUNKS_COHESION))
    else:
        indices_evaluados = list(range(n_total))

    chunks_eval = [chunks[i] for i in indices_evaluados]
    frases_por_chunk = [_dividir_en_frases(c) for c in chunks_eval]

    # Deduplicar: codificar cada frase única una sola vez.
    frases_unicas = sorted(set(f for frs in frases_por_chunk for f in frs))
    if not frases_unicas:
        return [None] * len(chunks_eval), indices_evaluados

    vecs = np.asarray(modelo.encode(frases_unicas), dtype=np.float32)
    normas = np.linalg.norm(vecs, axis=1, keepdims=True)
    normas[normas == 0] = 1.0
    vecs = vecs / normas
    vec_de_frase = dict(zip(frases_unicas, vecs))

    resultado = []
    for frs in frases_por_chunk:
        n = len(frs)
        if n < 2:
            resultado.append(None)
        else:
            M = np.vstack([vec_de_frase[f] for f in frs])
            sims = M @ M.T
            resultado.append(float(sims[np.triu_indices(n, k=1)].mean()))
    return resultado, indices_evaluados


def _texto_de_chunk(c):
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        for clave in ("texto", "text", "content", "page_content", "chunk"):
            if clave in c:
                return _texto_de_chunk(c[clave])
        raise TypeError(f"Chunk dict sin clave de texto reconocible. Claves: {list(c.keys())}")
    if hasattr(c, "page_content"):
        return c.page_content
    if isinstance(c, (tuple, list)):
        partes = []
        for p in c:
            try:
                sub = _texto_de_chunk(p)
                if sub and sub.strip():
                    partes.append(sub)
            except TypeError:
                continue
        if partes:
            return " ".join(partes)
    raise TypeError(f"No sé extraer texto de un chunk de tipo {type(c)}: {repr(c)[:150]}")


def metricas_estrategia(chunks, modelo, palabras_corpus):
    chunks = [_texto_de_chunk(c) for c in chunks]
    palabras = [len(c.split()) for c in chunks]
    cohesiones, indices_evaluados = cohesiones_por_chunk(chunks, modelo)
    coh = [v for v in cohesiones if v is not None]
    return {
        "n_chunks":       len(chunks),
        "n_muestra_coh":  len(indices_evaluados),
        "pal_min":        min(palabras) if palabras else 0,
        "pal_media":      statistics.mean(palabras) if palabras else 0,
        "pal_mediana":    statistics.median(palabras) if palabras else 0,
        "pal_max":        max(palabras) if palabras else 0,
        "pct_ini_limpio": 100 * sum(empieza_limpio(c) for c in chunks) / len(chunks) if chunks else 0,
        "pct_fin_limpio": 100 * sum(termina_limpio(c) for c in chunks) / len(chunks) if chunks else 0,
        "cohesion_media": (sum(coh) / len(coh)) if coh else float('nan'),
        "huerfanos":      sum(1 for p in palabras if p < MIN_PALABRAS),
        # Suma de palabras de todos los chunks dividida entre las del corpus.
        # 1,00 = sin repetición. Valores altos = la estrategia duplica texto
        # por efecto del solapamiento e infla el resto de métricas.
        "factor_solape":  sum(palabras) / palabras_corpus if palabras_corpus else 0,
    }


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN E INFORME
# ─────────────────────────────────────────────────────────────────────────────
def main():
    pdfs = sorted(Path(CORPUS).glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No hay PDFs en {Path(CORPUS).resolve()}")

    modelo = Codificador()

    print(f"Extrayendo y limpiando {len(pdfs)} documento(s)...")
    documentos = {}
    for pdf in pdfs:
        texto = preparar_texto(pdf)
        documentos[pdf.stem] = texto
        nf = len(_dividir_en_frases(texto))
        print(f"  {pdf.stem:<38} {len(texto.split()):>6} palabras | "
              f"{nf:>4} frases | {len(texto.split())/max(nf,1):>5.1f} pal/frase")

    palabras_corpus = sum(len(t.split()) for t in documentos.values())
    frases_corpus = sum(len(_dividir_en_frases(t)) for t in documentos.values())
    print(f"\nCorpus: {palabras_corpus} palabras | {frases_corpus} frases\n")

    # ── REGISTRO DE ESTRATEGIAS ──────────────────────────────────────────────
    # La etiqueta D decía antes "por tamaño respetando frases" pero la función
    # registrada era trocear_recursiva: por eso en la memoria parecía faltar la
    # recursiva y sobrar una estrategia que no se describe en ningún apartado.
    #
    # trocear_por_sentencias usaba solape_frases=2 por defecto. Con frases
    # largas eso duplica más texto que el propio contenido nuevo del chunk y
    # su fila deja de ser comparable con el resto.
    estrategias = {
        "A · por caracteres":
            lambda t: trocear_por_caracteres(t, tam=815, solape=125),
        "B · por palabras":
            lambda t: trocear_por_palabra(t, tam=135, solape=20),
        "C · por frases":
            lambda t: trocear_por_sentencias(t, tam=105, solape_frases=0),
        "D · recursiva":
            lambda t: trocear_recursiva(t, tam=790, solape=120),
        "E · semántica (elegida)":
            lambda t: trocear_semantica(t, modelo, percentil=PERCENTIL,
                                        tam_max=TAM_MAX, tam_min=TAM_MIN),
    }
    # ─────────────────────────────────────────────────────────────────────────

    resultados = {}
    for nombre, fn in estrategias.items():
        print(f"Troceando y midiendo: {nombre}")
        # Cada documento se trocea por separado, igual que en indexar.py, y
        # después se agregan los fragmentos de todos ellos.
        chunks, por_doc = [], {}
        for doc, texto in documentos.items():
            trozos = [_texto_de_chunk(c) for c in fn(texto)]
            por_doc[doc] = len(trozos)
            chunks.extend(trozos)
        resultados[nombre] = {
            "chunks": chunks,
            "por_doc": por_doc,
            "met": metricas_estrategia(chunks, modelo, palabras_corpus),
        }

    # ── Informe Markdown ──────────────────────────────────────────────────────
    L = []
    L.append("# Evaluación intrínseca de fragmentación\n")
    L.append("Sin preguntas: se mide la calidad de los fragmentos en sí. Extracción "
             "y limpieza son idénticas entre estrategias; lo único que cambia es cómo "
             "se trocea. Los embeddings se calculan con el mismo modelo cuantizado "
             "que construye el índice.\n")

    L.append("## Corpus de partida\n")
    L.append("| Documento | Palabras | Frases | Palabras/frase |")
    L.append("|---|---:|---:|---:|")
    for doc, texto in documentos.items():
        nf = len(_dividir_en_frases(texto))
        L.append(f"| {doc} | {len(texto.split())} | {nf} | {len(texto.split())/max(nf,1):.1f} |")
    L.append(f"| **Total** | **{palabras_corpus}** | **{frases_corpus}** | "
             f"**{palabras_corpus/max(frases_corpus,1):.1f}** |\n")

    L.append("## Métricas por estrategia\n")
    L.append("| Estrategia | Nº chunks | Palabras (mín/med/máx) | Inicio limpio | "
             "Fin limpio | Cohesión intra | Huérfanos | Factor solape |")
    L.append("|---|---:|:--:|---:|---:|---:|---:|---:|")
    for nombre, r in resultados.items():
        m = r["met"]
        coh = (f"{m['cohesion_media']:.3f} (n={m['n_muestra_coh']})"
               if m['n_muestra_coh'] < m['n_chunks']
               else f"{m['cohesion_media']:.3f}")
        L.append(f"| {nombre} | {m['n_chunks']} | "
                 f"{m['pal_min']}/{m['pal_media']:.0f}/{m['pal_max']} | "
                 f"{m['pct_ini_limpio']:.0f}% | {m['pct_fin_limpio']:.0f}% | "
                 f"{coh} | {m['huerfanos']} | {m['factor_solape']:.2f} |")

    L.append("\n### Reparto de fragmentos por documento\n")
    L.append("| Estrategia | " + " | ".join(documentos.keys()) + " |")
    L.append("|---|" + "---:|" * len(documentos))
    for nombre, r in resultados.items():
        L.append(f"| {nombre} | " + " | ".join(str(r["por_doc"][d]) for d in documentos) + " |")

    L.append("\n**Cómo leer la tabla:**\n")
    L.append("- *Palabras*: mínimo, **media** y máximo por fragmento. En las estrategias "
             "de tamaño fijo el mínimo corresponde al último fragmento de cada documento, "
             "que recoge el texto sobrante y es más corto que el resto.")
    L.append("- *Inicio/fin limpio*: % de chunks que empiezan y terminan en un límite "
             "de frase. Mide si la estrategia respeta las frases.")
    L.append("- *Cohesión intra*: similitud coseno media entre todos los pares de frases "
             "de un mismo chunk, calculada con el modelo de embeddings del proyecto. "
             "Alta = el fragmento habla de una sola cosa. **No la maximices sola**: "
             "chunks minúsculos dan cohesión alta pero son inútiles; léela junto al tamaño.")
    L.append(f"- *Huérfanos*: chunks con menos de {MIN_PALABRAS} palabras.")
    L.append("- *Factor de solape*: cuánto texto se contabiliza respecto al corpus "
             "original. 1,00 significa sin repetición. **Si dos estrategias tienen "
             "factores muy distintos, sus cifras no son comparables entre sí.**\n")

    L.append("## Filas para la tabla LaTeX\n")
    L.append("```latex")
    for nombre, r in resultados.items():
        m = r["met"]
        etiqueta = nombre.split("· ")[-1].capitalize()
        L.append(f"        {etiqueta:<26} & {m['n_chunks']:>3} & "
                 f"{m['pal_min']}/{m['pal_media']:.0f}/{m['pal_max']:<10} & "
                 f"{m['pct_ini_limpio']:.0f}\\% & {m['pct_fin_limpio']:.0f}\\% & "
                 f"{m['cohesion_media']:.3f} & {m['huerfanos']} & "
                 f"{m['factor_solape']:.2f} \\\\")
    L.append("```\n")

    L.append("## Muestra de fragmentos\n")
    for nombre, r in resultados.items():
        L.append(f"### {nombre}\n")
        for k, c in enumerate(r["chunks"][:N_MUESTRA]):
            extracto = c if len(c) <= 400 else c[:400] + " […]"
            L.append(f"{k + 1}. ({len(c.split())} pal) {extracto}\n")

    informe = SALIDA_EVAL / "informe_fragmentacion.md"
    informe.write_text("\n".join(L), encoding="utf-8")
    print(f"\nInforme generado en: {informe.resolve()}")

    # ── Aviso de comparabilidad ──────────────────────────────────────────────
    solapes = {n: r["met"]["factor_solape"] for n, r in resultados.items()}
    print("\nFactores de solape:")
    for n, s in sorted(solapes.items(), key=lambda x: -x[1]):
        print(f"  {n:<28} {s:.2f}")

    if max(solapes.values()) - min(solapes.values()) > UMBRAL_SOLAPE:
        peor = max(solapes, key=solapes.get)
        print(f"\n[AVISO] Los factores de solape difieren en más de {UMBRAL_SOLAPE}.")
        print(f"        '{peor}' cubre bastante más texto que el resto, así que sus")
        print(f"        métricas no son comparables. Reduce su solapamiento antes de")
        print(f"        llevar la tabla a la memoria.")


if __name__ == "__main__":
    main()