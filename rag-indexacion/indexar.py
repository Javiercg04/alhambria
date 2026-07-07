from pathlib import Path
import numpy as np
import sqlite3
import os

from src.chunking import trocear_por_sentencias
from src.extraccion import limpiar_texto_completo, extraer_texto
from src.indexado import generar_embedding, guardar_indice

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


BASE = Path(__file__).parent
CORPUS = BASE / "corpus"
SALIDA = BASE / "salida"
SALIDA.mkdir(exist_ok=True)


def main():
    pdfs = sorted(CORPUS.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {CORPUS.resolve()}. Copia ahi tu corpus.")
        return

    registros = []                                     # (texto_chunk, documento)
    for pdf in pdfs:
        texto = limpiar_texto_completo(extraer_texto(pdf))
        for c in trocear_por_sentencias(texto):
            registros.append((c, pdf.stem))
    print(f"{len(registros)} chunks generados de {len(pdfs)} PDF(s)")

    vectores = generar_embedding([t for t, _ in registros])

    guardar_indice(registros, vectores, SALIDA)

    n_vec = np.load(SALIDA / "vectores.npy").shape[0]
    n_bd = sqlite3.connect(SALIDA / "rag.db").execute(
        "SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(f"Indice guardado en {SALIDA.resolve()}")
    print(f"vectors.npy: {n_vec} | rag.db: {n_bd} | cuadra: {n_vec == n_bd}")


if __name__ == "__main__":
    main()