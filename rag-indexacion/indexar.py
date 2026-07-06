from pathlib import Path
import numpy as np
import sqlite3

from src.chunking import trocear_por_palabra
from src.extraccion import limpiar_texto, extraer_texto
from src.indexado import generar_embedding, guardar_indice


BASE = Path(__file__).parent
CORPUS = BASE / "corpus"
SALIDA = BASE / "salida"
SALIDA.mkdir(exist_ok=True)


def main():
    pdfs = sorted(CORPUS.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {CORPUS.resolve()}. Copia ahi tu corpus.")
        return

    # 1-3. Extraccion + limpieza + chunking de todo el corpus
    registros = []                                     # (texto_chunk, documento)
    for pdf in pdfs:
        texto = limpiar_texto(extraer_texto(pdf))
        for c in trocear_por_palabra(texto):
            registros.append((c, pdf.stem))
    print(f"{len(registros)} chunks generados de {len(pdfs)} PDF(s)")

    # 4. Embeddings
    vectores = generar_embedding([t for t, _ in registros])

    # 5. Persistencia
    guardar_indice(registros, vectores, SALIDA)

    # Verificacion: nº de vectores == nº de chunks guardados
    n_vec = np.load(SALIDA / "vectors.npy").shape[0]
    n_bd = sqlite3.connect(SALIDA / "rag.db").execute(
        "SELECT COUNT(*) FROM chunks").fetchone()[0]
    print(f"Indice guardado en {SALIDA.resolve()}")
    print(f"vectors.npy: {n_vec} | rag.db: {n_bd} | cuadra: {n_vec == n_bd}")


if __name__ == "__main__":
    main()