# indexado.py

from sentence_transformers import SentenceTransformer
import onnxruntime as ort
from onnxruntime_extensions import get_library_path
import sqlite3
import numpy as np

_opts = ort.SessionOptions()
_opts.register_custom_ops_library(get_library_path())
tok = ort.InferenceSession("salida/modelo/tokenizer/tokenizer.onnx", _opts)

emb = ort.InferenceSession("salida/modelo/bge-m3.onnx")

#MODELO = "sentence-transformers/   "
#MODELO = "sentence-transformers/all-MiniLM-L6-v2"
MODELO = "BAAI/bge-m3"
def generar_embedding(textos):
    vecs = []
    for t in textos:
        ids = tok.run(None, {tok.get_inputs()[0].name: np.array([t])})
        ids_arr = np.asarray(ids[0]).reshape(1, -1).astype(np.int64)
        mask = np.ones_like(ids_arr)
        out = emb.run(None, {"input_ids": ids_arr, "attention_mask": mask})
        v = np.asarray(out[0]).reshape(-1).astype(np.float32)
        vecs.append(v / (np.linalg.norm(v) or 1))
    return np.array(vecs, dtype=np.float32)

def guardar_indice(registros, vectores, salida):
    assert len(registros) == len(vectores)

    con = sqlite3.connect(salida / "rag_v3.db")
    con.execute("DROP TABLE IF EXISTS chunks")
    con.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, texto TEXT NOT NULL, " \
    "embedding BLOB NOT NULL, fuente TEXT NOT NULL)")
    con.executemany(
        "INSERT INTO chunks(id, texto, embedding, fuente) VALUES (?, ?, ?, ?)",
        [(i, texto, vec.astype(np.float32).tobytes(), fuente)
        for i, ((texto, fuente), vec) in enumerate(zip(registros, vectores))]
    )
    con.commit()
    con.close()
