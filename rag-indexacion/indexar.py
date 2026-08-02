from pathlib import Path
import numpy as np
import sqlite3
import os
from sentence_transformers import SentenceTransformer

from src.chunking import trocear_semantica
from src.extraccion import limpiar_texto_completo, extraer_texto
from src.indexado import generar_embedding, guardar_indice

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
#os.environ["HF_HUB_OFFLINE"] = "1"

BASE = Path(__file__).parent
CORPUS = BASE / "corpus"
SALIDA = BASE / "salida" / "indice"
SALIDA.mkdir(exist_ok=True)

MODELO = "BAAI/bge-m3"
modelo = SentenceTransformer(MODELO)

def main():
    pdfs = sorted(CORPUS.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {CORPUS.resolve()}. Copia ahi tu corpus.")
        return

    registros = []                                     # (texto_chunk, documento)
    for pdf in pdfs:
        texto = limpiar_texto_completo(extraer_texto(pdf))
        for c in trocear_semantica(texto,modelo):
            registros.append((c, pdf.stem))
    print(f"{len(registros)} chunks generados de {len(pdfs)} PDF(s)")

    vectores = generar_embedding([t for t, _ in registros])

    guardar_indice(registros, vectores, SALIDA)

    con = sqlite3.connect(SALIDA / "rag.db")
    n_bd = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    blob = con.execute("SELECT embedding FROM chunks ORDER BY id LIMIT 1").fetchone()[0]
    con.close()
    v = np.frombuffer(blob, dtype=np.float32)
    print(f"Indice guardado en {SALIDA.resolve()}")
    print(f"rag.db: {n_bd} chunks | dimension: {v.shape[0]} | norma: {np.linalg.norm(v):.4f}")

if __name__ == "__main__":
    main()