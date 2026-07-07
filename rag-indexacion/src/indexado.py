# indexado.py

from sentence_transformers import SentenceTransformer
import sqlite3
import numpy as np

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def generar_embedding(textos):
    modelo = SentenceTransformer(MODELO)
    return modelo.encode(textos, normalize_embeddings=True, show_progress_bar=True)


def guardar_indice(registros, vectores, salida):
    np.save(salida / "vectores.npy", vectores)

    con = sqlite3.connect(salida / "rag.db")
    con.execute("DROP TABLE IF EXISTS chunks")
    con.execute("CREATE TABLE chunks(id INTEGER PRIMARY KEY, texto TEXT, doc TEXT)")
    con.executemany(
        "INSERT INTO chunks(id, texto, doc) VALUES (?, ?, ?)",
        [(i, t, d) for i, (t, d) in enumerate(registros)],
    )
    con.commit()
    con.close()
