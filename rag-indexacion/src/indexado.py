# indexado.py

from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np

#MODELO = "sentence-transformers/   "
#MODELO = "sentence-transformers/all-MiniLM-L6-v2"
MODELO = "BAAI/bge-m3"
def generar_embedding(textos):
    modelo = SentenceTransformer(MODELO)
    return modelo.encode(textos, normalize_embeddings=True, show_progress_bar=True)

def guardar_indice(registros, vectores, salida):
    assert len(registros) == len(vectores)

    con = sqlite3.connect(salida / "rag.db")
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
