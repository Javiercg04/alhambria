"""
construir_indices.py

Construye los dos indices del experimento de recuperacion garantizando que la
unica diferencia entre ellos es el modelo de embeddings.

El troceado semantico usa el codificador para decidir donde cortar, asi que si
cada indice se construyera ejecutando el pipeline completo con su modelo, los
dos indices tendrian fragmentos distintos ademas de vectores distintos. La
comparacion mediria las dos cosas a la vez.

Por eso aqui el corpus se trocea UNA sola vez, con el modelo cuantizado, que es
el que va embarcado en la aplicacion. Los fragmentos resultantes se guardan en
disco y se vectorizan despues con los dos modelos.

Uso:
    python construir_indices.py --corpus corpus --salida salida
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path

import numpy as np


def cargar_modulos(ruta_src):
    sys.path.insert(0, str(Path(ruta_src).resolve()))
    from extraccion import extraer_texto, limpiar_texto_completo
    from chunking import trocear_semantica
    return extraer_texto, limpiar_texto_completo, trocear_semantica


def codificador(ruta_onnx, ruta_tokenizer):
    """Codificador ONNX. Mismo procedimiento que indexado.py."""
    import onnxruntime as ort
    from onnxruntime_extensions import get_library_path

    opciones = ort.SessionOptions()
    opciones.register_custom_ops_library(get_library_path())
    tok = ort.InferenceSession(str(ruta_tokenizer), opciones)
    emb = ort.InferenceSession(str(ruta_onnx))

    class Codificador:
        def encode(self, textos):
            vectores = []
            for t in textos:
                ids = tok.run(None, {tok.get_inputs()[0].name: np.array([t])})
                ids_arr = np.asarray(ids[0]).reshape(1, -1).astype(np.int64)
                mask = np.ones_like(ids_arr)
                salida = emb.run(None, {"input_ids": ids_arr,
                                        "attention_mask": mask})
                v = np.asarray(salida[0]).reshape(-1).astype(np.float32)
                vectores.append(v / (np.linalg.norm(v) or 1.0))
            return np.array(vectores, dtype=np.float32)

    return Codificador()


def trocear_corpus(carpeta_corpus, modelo, funciones):
    extraer_texto, limpiar_texto_completo, trocear_semantica = funciones
    pdfs = sorted(Path(carpeta_corpus).glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No hay PDFs en {carpeta_corpus}")

    registros = []
    for pdf in pdfs:
        texto = limpiar_texto_completo(extraer_texto(pdf))
        fragmentos = trocear_semantica(texto, modelo)
        registros.extend((c, pdf.stem) for c in fragmentos)
        print(f"  {pdf.stem:<34} {len(fragmentos):>4} fragmentos")

    return registros


def guardar(registros, vectores, ruta_db):
    con = sqlite3.connect(ruta_db)
    con.execute("DROP TABLE IF EXISTS chunks")
    con.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, texto TEXT NOT NULL, "
                "embedding BLOB NOT NULL, fuente TEXT NOT NULL)")
    con.executemany(
        "INSERT INTO chunks(id, texto, embedding, fuente) VALUES (?, ?, ?, ?)",
        [(i, texto, vec.astype(np.float32).tobytes(), fuente)
         for i, ((texto, fuente), vec) in enumerate(zip(registros, vectores))])
    con.commit()

    n = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    blob = con.execute("SELECT embedding FROM chunks ORDER BY id LIMIT 1").fetchone()[0]
    v = np.frombuffer(blob, dtype=np.float32)
    print(f"  {ruta_db.name}: {n} chunks | dim {v.shape[0]} | norma {np.linalg.norm(v):.4f}")
    con.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="corpus")
    parser.add_argument("--salida", default="salida")
    parser.add_argument("--src", default="src")
    args = parser.parse_args()

    salida = Path(args.salida)
    modelo_dir = salida / "modelo"
    indice_dir = salida / "indice"
    indice_dir.mkdir(parents=True, exist_ok=True)

    tokenizer = modelo_dir / "tokenizer" / "tokenizer.onnx"
    onnx_int8 = modelo_dir / "bge-m3.int8.onnx"
    onnx_fp32 = modelo_dir / "bge-m3.onnx"

    for ruta in (tokenizer, onnx_int8, onnx_fp32):
        if not ruta.exists():
            raise SystemExit(f"Falta {ruta}")

    funciones = cargar_modulos(args.src)

    print("\n[1/3] Troceado semantico (una sola vez, con el modelo int8)")
    cod_int8 = codificador(onnx_int8, tokenizer)
    registros = trocear_corpus(args.corpus, cod_int8, funciones)
    print(f"  total: {len(registros)} fragmentos")

    ruta_frag = indice_dir / "fragmentos.json"
    ruta_frag.write_text(
        json.dumps([{"texto": t, "fuente": f} for t, f in registros],
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  fragmentos guardados en {ruta_frag}")

    textos = [t for t, _ in registros]

    print("\n[2/3] Vectorizando con el modelo cuantizado (int8)")
    guardar(registros, cod_int8.encode(textos), indice_dir / "rag_v4.db")

    print("\n[3/3] Vectorizando los MISMOS fragmentos con el modelo fp32")
    cod_fp32 = codificador(onnx_fp32, tokenizer)
    guardar(registros, cod_fp32.encode(textos), indice_dir / "rag_v4_fp32.db")

    print("\nListo. Los dos indices contienen los mismos fragmentos en el mismo "
          "orden, por lo que la unica variable es el modelo de embeddings.")


if __name__ == "__main__":
    main()