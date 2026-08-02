import os, json, sqlite3
import numpy as np

from transformers import AutoTokenizer
from pathlib import Path

CARPETA = os.path.join("..", "salida", "modelo", "tokenizer")
RUTA_TOKEN = os.path.join(CARPETA)

CARPETA_INDICE = os.path.join("..", "salida", "indice")
RUTA_DB = os.path.join(CARPETA_INDICE,"rag.db")

# Guardado el tokenizer.json
tok = AutoTokenizer.from_pretrained("BAAI/bge-m3").save_pretrained(RUTA_TOKEN)

# Guardado del indice.json
con = sqlite3.connect(RUTA_DB)
filas = con.execute("SELECT texto, embedding FROM chunks ORDER BY id").fetchall()
con.close()

index = []
for texto, blob in filas:
    vec = np.frombuffer(blob, dtype=np.float32)
    index.append({"texto": texto, "embedding": vec.tolist()})

json.dump(index, open("index.json", "w"), ensure_ascii="utf-8")
print(f"index.json: {len(index)} fragmentos, dim {len(index[0]['embedding'])}")