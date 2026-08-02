from pathlib import Path
import re, sys, os
import statistics
import numpy as np
from sentence_transformers import SentenceTransformer

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)

# ╔═══════════════════════════════════════════════════════════════════════════╗
# ║ IMPORTS DE TU CÓDIGO — pon aquí los nombres REALES de tus funciones        ║
# ╚═══════════════════════════════════════════════════════════════════════════╝
# Extracción y limpieza (src/extraccion.py). Si es una sola función, importa esa
# y adapta preparar_texto() más abajo.
from extraccion import extraer_texto, limpiar_texto_completo

# TODAS tus funciones de troceado (src/chunking.py). Sustituye estos nombres por
# los tuyos reales. Luego, abajo en 'estrategias', las registras para compararlas.
from chunking import (
    trocear_recursiva,
    trocear_semantica,
    trocear_por_palabra,
    trocear_por_caracteres,
    trocear_por_sentencias,
)
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────────────────────────────────────
BASE        = Path(__file__).parent
PDF         = BASE / ".." / "corpus" / "N_22_08.pdf"     # <- el único PDF a evaluar
SALIDA_EVAL = BASE / "salida_eval"
SALIDA_EVAL.mkdir(exist_ok=True)

MODELO_EMB   = "BAAI/bge-m3"    # el mismo que uses en la app (por comparabilidad)
MIN_PALABRAS = 15              # bajo esto, un chunk se considera "huérfano"
N_MUESTRA    = 4              # nº de chunks de ejemplo a volcar por estrategia


def preparar_texto(ruta):
    """Extrae y limpia usando TU código de src. Si tienes una sola función que
    hace ambas cosas, sustituye estas dos llamadas por la tuya."""
    return limpiar_texto_completo(extraer_texto(ruta))

ABREVIATURAS = {
    "sr", "sra", "dr", "dra", "d", "dña", "ud", "uds", "prof", "profa",
    "pag", "pags", "pág", "págs", "vol", "vols", "num", "núm", "art", "arts",
    "cap", "caps", "fig", "figs", "ms", "mss", "p", "pp", "ej", "etc",
    "aprox", "g", "h", "r", "s", "n", "trad", "ed", "eds", "coord", "coords",
    "vid", "cf", "op", "loc", "cit", "ibid", "cfr",
}
 
def _dividir_en_frases(texto):
    """Divide el texto en frases usando . ! ? seguidos de espacio y mayuscula,
    PERO no corta si la palabra justo antes del punto es una abreviatura
    conocida o una sola letra (iniciales de nombres, siglas, transliteraciones
    arabes tipo 'Muhammad b. Yusuf b. Nasr' o fechas '(g. 1232-1273)')."""
    patron = re.compile(r'([.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«])')
    frases, pos = [], 0
    for m in patron.finditer(texto):
        fin_signo = m.end(1)
        antes = texto[:fin_signo - 1]
        match_palabra = re.search(r'(\w+)$', antes)
        palabra = match_palabra.group(1).lower() if match_palabra else ""
        # Solo se trata como abreviatura si HAY una palabra justo antes del
        # punto y esa palabra es corta/conocida. Si no hay palabra (el punto
        # va tras un paréntesis, comilla, número suelto, etc.), sí es fin de
        # frase real y hay que cortar.
        es_abreviatura_o_inicial = bool(palabra) and (len(palabra) <= 1 or palabra in ABREVIATURAS)
        if es_abreviatura_o_inicial:
            continue  # no es fin de frase real, seguimos acumulando
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

MAX_CHUNKS_COHESION = 300  # si una estrategia genera más chunks que esto, la cohesión
                           # se calcula sobre una muestra aleatoria (semilla fija) en vez
                           # de sobre todos. El resto de métricas (tamaño, cortes limpios,
                           # huérfanos) sí se calculan sobre el 100% de los chunks: son
                           # gratis, no necesitan al modelo de embeddings.
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

    # Deduplicar: codificar cada frase única una sola vez
    frases_unicas = sorted(set(f for frs in frases_por_chunk for f in frs))
    if not frases_unicas:
        return [None] * len(chunks_eval), indices_evaluados

    vecs_unicas = modelo.encode(frases_unicas, normalize_embeddings=True,
                                show_progress_bar=True, batch_size=batch_size)
    vec_de_frase = dict(zip(frases_unicas, vecs_unicas))

    resultado = []
    for frs in frases_por_chunk:
        n = len(frs)
        if n < 2:
            resultado.append(None)
        else:
            vecs = [vec_de_frase[f] for f in frs]
            sims = [float(np.dot(vecs[a], vecs[b]))
                    for a in range(n) for b in range(a + 1, n)]
            resultado.append(sum(sims) / len(sims) if sims else None)
    return resultado, indices_evaluados

def _texto_de_chunk(c):
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        for clave in ("texto", "text", "content", "page_content", "chunk"):
            if clave in c:
                return _texto_de_chunk(c[clave])
        raise TypeError(f"Chunk dict sin clave de texto reconocible. Claves: {list(c.keys())}")
    if hasattr(c, "page_content"):          # Document de LangChain
        return c.page_content
    if isinstance(c, (tuple, list)):
        partes = []
        for p in c:
            try:
                sub = _texto_de_chunk(p)      # recursivo: soporta cualquier anidamiento
                if sub and sub.strip():
                    partes.append(sub)
            except TypeError:
                continue                       # elemento no reconocible (p. ej. metadata) -> se ignora
        if partes:
            return " ".join(partes)
    raise TypeError(f"No sé extraer texto de un chunk de tipo {type(c)}: {repr(c)[:150]}")


def metricas_estrategia(chunks, modelo):
    chunks = [_texto_de_chunk(c) for c in chunks]   # normaliza a str una sola vez
    palabras = [len(c.split()) for c in chunks]
    cohesiones, indices_evaluados = cohesiones_por_chunk(chunks, modelo)
    coh = [v for v in cohesiones if v is not None]
    return {
        "n_chunks":       len(chunks),
        "n_muestra_coh":  len(indices_evaluados),   # cuántos chunks entraron en la cohesión
        "pal_min":        min(palabras) if palabras else 0,
        "pal_mediana":    statistics.median(palabras) if palabras else 0,
        "pal_max":        max(palabras) if palabras else 0,
        "pct_ini_limpio": 100 * sum(empieza_limpio(c) for c in chunks) / len(chunks) if chunks else 0,
        "pct_fin_limpio": 100 * sum(termina_limpio(c) for c in chunks) / len(chunks) if chunks else 0,
        "cohesion_media": (sum(coh) / len(coh)) if coh else float('nan'),
        "huerfanos":      sum(1 for p in palabras if p < MIN_PALABRAS),
    }


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN E INFORME
# ─────────────────────────────────────────────────────────────────────────────
def main():
    if not PDF.exists():
        raise FileNotFoundError(f"No encuentro el PDF en {PDF.resolve()}")

    print(f"Cargando modelo de embeddings ({MODELO_EMB})...")
    modelo = SentenceTransformer(MODELO_EMB)

    print(f"Extrayendo y limpiando {PDF.name} (con tu código de src)...")
    texto = preparar_texto(PDF)

    # ── REGISTRO DE ESTRATEGIAS ──────────────────────────────────────────────
    # Clave = nombre que saldrá en el informe. Valor = tu función de troceado.
    # Ajusta parámetros y nombres a los tuyos. Si alguna necesita el modelo de
    # embeddings (p. ej. la semántica), pásaselo: lambda t: trocear_semantico(t, modelo)
    estrategias = {
        "A · por caracteres":
            lambda t: trocear_por_caracteres(t),
        "B · por palabras (actual)":
            lambda t: trocear_por_palabra(t),
        "C · por frases":
            lambda t: trocear_por_sentencias(t),
        "D · por tamaño respetando frases":
            lambda t: trocear_recursiva(t),
        "E · semántico":
            lambda t: trocear_semantica(t, modelo),
    }
    # ─────────────────────────────────────────────────────────────────────────

    resultados = {}
    for nombre, fn in estrategias.items():
        print(f"Troceando y midiendo: {nombre}")
        chunks = [_texto_de_chunk(c) for c in fn(texto)]   # normaliza aquí, una vez
        resultados[nombre] = {"chunks": chunks, "met": metricas_estrategia(chunks, modelo)}

    # ── Informe Markdown ──────────────────────────────────────────────────────
    L = []
    L.append(f"# Evaluación intrínseca de fragmentación — {PDF.name}\n")
    L.append("Sin preguntas: se mide la calidad de los fragmentos en sí. Extracción "
             "y limpieza son idénticas entre estrategias (tu código de src); lo único "
             "que cambia es cómo se trocea.\n")

    L.append("## Métricas por estrategia\n")
    L.append("| Estrategia | Nº chunks | Palabras (mín/med/máx) | Inicio limpio | Fin limpio | Cohesión intra (muestra) | Huérfanos |")
    L.append("|---|---:|:--:|---:|---:|---:|---:|")
    for nombre, r in resultados.items():
        m = r["met"]
        muestra = (f"{m['cohesion_media']:.3f} (n={m['n_muestra_coh']})"
                  if m['n_muestra_coh'] < m['n_chunks']
                  else f"{m['cohesion_media']:.3f}")
        L.append(f"| {nombre} | {m['n_chunks']} | "
                 f"{m['pal_min']}/{m['pal_mediana']:.0f}/{m['pal_max']} | "
                 f"{m['pct_ini_limpio']:.0f}% | {m['pct_fin_limpio']:.0f}% | "
                 f"{muestra} | {m['huerfanos']} |")

    L.append("\n**Cómo leer la tabla:**\n")
    L.append("- *Inicio/fin limpio*: % de chunks que empiezan y terminan en un límite "
             "de frase. Mide si la estrategia respeta las frases. Por caracteres sale "
             "bajo; por frases, cerca del 100%.")
    L.append("- *Cohesión intra*: cómo de parecidas son entre sí las frases de un mismo "
             "chunk. Alta = habla de una sola cosa. **No la maximices sola**: chunks "
             "minúsculos dan cohesión alta pero son inútiles; léela junto al tamaño.")
    L.append(f"- *Huérfanos*: chunks con menos de {MIN_PALABRAS} palabras.\n")

    L.append("> La mejor fragmentación combina a la vez cortes limpios, cohesión "
             "razonable y tamaño útil sin huérfanos. La tabla orienta; la muestra decide.\n")

    L.append("## Muestra de fragmentos (léelos y juzga si cada uno es una idea completa)\n")
    for nombre, r in resultados.items():
        L.append(f"### {nombre}\n")
        for k, c in enumerate(r["chunks"][:N_MUESTRA]):
            extracto = c if len(c) <= 400 else c[:400] + " […]"
            L.append(f"{k + 1}. ({len(c.split())} pal) {extracto}\n")

    informe = SALIDA_EVAL / "informe_fragmentacion.md"
    informe.write_text("\n".join(L), encoding="utf-8")
    print(f"\nInforme generado en: {informe.resolve()}")


if __name__ == "__main__":
    main()