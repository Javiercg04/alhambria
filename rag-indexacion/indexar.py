from pathlib import Path
from src import indexado
import numpy as np
import sqlite3
import os


from src.chunking import trocear_semantica
from src.extraccion import limpiar_texto_completo, extraer_texto
from src.indexado import generar_embedding, guardar_indice

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
#os.environ["HF_HUB_OFFLINE"] = "1"

BASE = Path(__file__).parent
CORPUS = BASE / "corpus"
SALIDA = BASE / "salida" / "indice"
SALIDA.mkdir(exist_ok=True)


def main():
    pdfs = sorted(CORPUS.glob("*.pdf"))
    if not pdfs:
        print(f"No hay PDFs en {CORPUS.resolve()}. Copia ahi tu corpus.")
        return

    registros = []                                     # (texto_chunk, documento)
    for pdf in pdfs:
        texto = limpiar_texto_completo(extraer_texto(pdf))
        for c in trocear_semantica(texto,indexado):
            registros.append((c, pdf.stem))
    print(f"{len(registros)} chunks generados de {len(pdfs)} PDF(s)")


    vectores = generar_embedding([t for t, _ in registros])

    guardar_indice(registros, vectores, SALIDA)

    con = sqlite3.connect(SALIDA / "rag_v4.db")
    n_bd = con.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    blob = con.execute("SELECT embedding FROM chunks ORDER BY id LIMIT 1").fetchone()[0]
    print(f"Indice guardado en {SALIDA.resolve()}")
    print(f"rag_v4.db: {n_bd} chunks | dimension: {np.frombuffer(blob, dtype=np.float32).shape[0]} "
          f"| norma: {np.linalg.norm(np.frombuffer(blob, dtype=np.float32)):.4f}")

    print("\nReparto por fuente:")
    for fuente, n, med, mn, mx in con.execute(
        "SELECT fuente, COUNT(*), AVG(LENGTH(texto)), MIN(LENGTH(texto)), MAX(LENGTH(texto)) "
        "FROM chunks GROUP BY fuente"
    ):
        print(f"  {fuente:<40} {n:>4} chunks | media {med:.0f} car | {mn}-{mx}")

    cortos = con.execute("SELECT COUNT(*) FROM chunks WHERE LENGTH(texto) < 250").fetchone()[0]
    print(f"\nChunks por debajo de 250 caracteres: {cortos}")
    con.close()

if __name__ == "__main__":
    main()