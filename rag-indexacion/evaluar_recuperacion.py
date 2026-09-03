"""
evaluar_recuperacion.py

Mide la calidad de la recuperacion del indice con recall@k y MRR.

Los fragmentos relevantes de cada pregunta no se identifican por id, sino por
un ancla: un trozo literal del texto donde esta la respuesta. El id de un chunk
cambia cada vez que se reindexa o se cambia la estrategia de troceado, asi que
anotar por id obliga a rehacer el conjunto de evaluacion. El ancla no cambia.

Si un ancla deja de encontrarse, el script falla en vez de devolver un numero
silenciosamente equivocado.

Por defecto codifica las preguntas con el generar_embedding de indexado.py, que
es el modelo con el que se construyo el indice. Para evaluar la otra variante
del modelo se pasan --onnx y --tokenizer apuntando al fichero correspondiente,
siempre contra el indice construido con ESE mismo modelo: mezclar un indice
fp32 con consultas int8 mide el desajuste entre ambos, no la recuperacion.

Uso:
    # variante embarcada en el APK
    python evaluar_recuperacion.py --db salida/indice/rag_v4.db \
                                   --golden golden.json --src src

    # variante sin cuantizar, sobre su propio indice
    python evaluar_recuperacion.py --db salida/indice/rag_v4_fp32.db \
                                   --golden golden.json \
                                   --onnx salida/modelo/bge-m3.onnx \
                                   --tokenizer salida/modelo/tokenizer/tokenizer.onnx
"""

import argparse
import csv
import json
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path

import numpy as np

VALORES_K = (1, 3, 5, 10)


def normalizar(texto):
    """Minusculas, sin tildes, sin puntuacion, espacios colapsados."""
    texto = unicodedata.normalize("NFD", texto.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", texto).strip()


def cargar_indice(ruta_db):
    con = sqlite3.connect(ruta_db)
    filas = con.execute(
        "SELECT id, texto, embedding, fuente FROM chunks ORDER BY id").fetchall()
    con.close()
    if not filas:
        raise SystemExit(f"{ruta_db} no contiene chunks.")

    ids = [f[0] for f in filas]
    textos = [f[1] for f in filas]
    vectores = np.stack([np.frombuffer(f[2], dtype=np.float32) for f in filas])
    fuentes = [f[3] for f in filas]
    return ids, textos, vectores, fuentes


def resolver_relevantes(preguntas, textos, fuentes):
    """
    Devuelve {id_pregunta: set(posiciones)} buscando cada ancla en los chunks.

    Aborta si algun ancla no aparece o si aparece en un documento distinto del
    esperado: las dos cosas significan que el conjunto de evaluacion ha dejado
    de corresponderse con el indice.
    """
    textos_norm = [normalizar(t) for t in textos]
    relevantes, problemas = {}, []

    for p in preguntas:
        posiciones = set()
        for ancla in p["anclas"]:
            ancla_norm = normalizar(ancla)
            encontradas = [i for i, t in enumerate(textos_norm) if ancla_norm in t]
            if not encontradas:
                problemas.append(f"[{p['id']}] ancla no encontrada: {ancla!r}")
            posiciones.update(encontradas)

        docs = {fuentes[i] for i in posiciones}
        if p.get("doc") and docs and docs != {p["doc"]}:
            problemas.append(
                f"[{p['id']}] esperaba {p['doc']}, las anclas caen en {sorted(docs)}")
        relevantes[p["id"]] = posiciones

    if problemas:
        raise SystemExit("El golden no cuadra con el indice:\n  " +
                         "\n  ".join(problemas))
    return relevantes


def evaluar(preguntas, relevantes, vectores, codificar):
    k_max = max(VALORES_K)
    resultados = []

    for p in preguntas:
        vec = np.asarray(codificar([p["q"]]), dtype=np.float32).reshape(-1)
        vec /= np.linalg.norm(vec) or 1.0

        similitudes = vectores @ vec
        ranking = np.argsort(similitudes)[::-1][:k_max]

        rel = relevantes[p["id"]]
        fila = {"id": p["id"], "pregunta": p["q"], "doc": p.get("doc", ""),
                "cifras": p.get("cifras", False), "n_relevantes": len(rel)}

        for k in VALORES_K:
            recuperados = set(int(i) for i in ranking[:k])
            fila[f"recall@{k}"] = len(recuperados & rel) / len(rel)

        primera = next((r + 1 for r, i in enumerate(ranking) if int(i) in rel), None)
        fila["posicion"] = primera or 0
        fila["rr"] = 1.0 / primera if primera else 0.0
        resultados.append(fila)

    return resultados


def codificador_onnx(ruta_onnx, ruta_tokenizer):
    """Codificador equivalente al de indexado.py, con el modelo que se indique."""
    import onnxruntime as ort
    from onnxruntime_extensions import get_library_path

    opciones = ort.SessionOptions()
    opciones.register_custom_ops_library(get_library_path())
    tok = ort.InferenceSession(str(ruta_tokenizer), opciones)
    emb = ort.InferenceSession(str(ruta_onnx))

    def codificar(textos):
        vectores = []
        for t in textos:
            ids = tok.run(None, {tok.get_inputs()[0].name: np.array([t])})
            ids_arr = np.asarray(ids[0]).reshape(1, -1).astype(np.int64)
            mask = np.ones_like(ids_arr)
            salida = emb.run(None, {"input_ids": ids_arr, "attention_mask": mask})
            vectores.append(np.asarray(salida[0]).reshape(-1).astype(np.float32))
        return np.array(vectores, dtype=np.float32)

    return codificar


def media(filas, campo):
    return sum(f[campo] for f in filas) / len(filas) if filas else 0.0


def informar(resultados):
    def bloque(titulo, filas):
        if not filas:
            return
        partes = " | ".join(f"recall@{k} {media(filas, f'recall@{k}'):.3f}"
                            for k in VALORES_K)
        print(f"{titulo:<34} n={len(filas):<3} {partes} | MRR {media(filas, 'rr'):.3f}")

    print(f"\n{'':<34} {'':<5} " + " ".join(f"    k={k}   " for k in VALORES_K))
    bloque("TOTAL", resultados)
    print()
    for doc in sorted({f["doc"] for f in resultados if f["doc"]}):
        bloque(doc[:32], [f for f in resultados if f["doc"] == doc])
    print()
    bloque("Consultas con cifras", [f for f in resultados if f["cifras"]])
    bloque("Consultas sin cifras", [f for f in resultados if not f["cifras"]])

    fallos = [f for f in resultados if f["recall@5"] < 1.0]
    if fallos:
        print(f"\nFallos con k=5 ({len(fallos)}):")
        for f in fallos:
            pos = f["posicion"] or "fuera del top 10"
            print(f"  [{f['id']}] {f['pregunta'][:62]:<64} 1er acierto: {pos}")
    else:
        print("\nSin fallos con k=5.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--golden", default="golden.json")
    parser.add_argument("--src", default="src",
                        help="carpeta que contiene indexado.py")
    parser.add_argument("--onnx", default=None,
                        help="modelo a usar en vez del de indexado.py")
    parser.add_argument("--tokenizer", default=None)
    parser.add_argument("--csv", default="resultados_recuperacion.csv")
    args = parser.parse_args()

    if args.onnx:
        if not args.tokenizer:
            raise SystemExit("--onnx requiere tambien --tokenizer")
        generar_embedding = codificador_onnx(args.onnx, args.tokenizer)
        print(f"Codificador: {args.onnx}")
    else:
        sys.path.insert(0, str(Path(args.src).resolve()))
        from indexado import generar_embedding
        print("Codificador: el de indexado.py")

    preguntas = json.loads(Path(args.golden).read_text(encoding="utf-8"))["preguntas"]
    ids, textos, vectores, fuentes = cargar_indice(args.db)
    print(f"Indice: {len(ids)} chunks de {vectores.shape[1]} dimensiones")
    print(f"Golden: {len(preguntas)} preguntas")

    relevantes = resolver_relevantes(preguntas, textos, fuentes)
    total = sum(len(v) for v in relevantes.values())
    print(f"Anclas resueltas: {total} fragmentos relevantes en total\n")

    resultados = evaluar(preguntas, relevantes, vectores, generar_embedding)
    informar(resultados)

    with open(args.csv, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultados[0].keys()))
        escritor.writeheader()
        escritor.writerows(resultados)
    print(f"\nDetalle por pregunta en {args.csv}")


if __name__ == "__main__":
    main()