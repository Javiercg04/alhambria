import os, csv, sys
import sqlite3
import numpy as np
import onnxruntime as ort
from pathlib import Path
from transformers import AutoTokenizer

MODELO = "BAAI/bge-m3"
BASE = os.path.dirname(os.path.abspath(__file__))
BASE2 = Path(__file__).resolve().parent     
RUTA_FP32 = os.path.join(BASE, "..", "salida", "modelo", "bge-m3.onnx")
RUTA_INT8 = os.path.join(BASE, "..", "salida", "modelo", "bge-m3.int8.onnx")
RUTA_DB   = os.path.join(BASE, "..", "salida", "indice", "rag.db")
PREGUNTAS = (BASE2 / ".." / ".." / "rag-consulta" / "preguntas_prueba").resolve()


tokenizer = AutoTokenizer.from_pretrained(MODELO)
sesion_fp32 = ort.InferenceSession(RUTA_FP32, providers=["CPUExecutionProvider"])
sesion_int8 = ort.InferenceSession(RUTA_INT8, providers=["CPUExecutionProvider"])

tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
print(tok("¿Quién mandó construir la Alhambra?")["input_ids"])

# --- Cargar el índice desde el BLOB ---
conexion = sqlite3.connect(RUTA_DB)
filas = conexion.execute("SELECT texto, embedding, fuente FROM chunks ORDER BY id").fetchall()
conexion.close()

ids    = [f[0] for f in filas]
textos = [f[1] for f in filas]
# ¡El dtype debe coincidir con el que usaste al guardar! (casi seguro float32)
indice = np.stack([np.frombuffer(f[1], dtype=np.float32) for f in filas])

# --- Función que vectoriza con una sesión ONNX cualquiera ---
def vectorizar(sesion, frase):
    e = tokenizer(frase, return_tensors="np", padding=True, truncation=True, max_length=512)
    return sesion.run(["embedding"], {
        "input_ids":      e["input_ids"].astype(np.int64),
        "attention_mask": e["attention_mask"].astype(np.int64),
    })[0][0]

def top_k(vec, k=5):
    sims = indice @ vec
    return [ids[i] for i in np.argsort(sims)[::-1][:k]]

def leer_preguntas(carpeta):
    if not carpeta.exists():
        raise SystemExit(f"No existe la carpeta {carpeta}")

    preguntas = []
    for f in sorted(carpeta.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() == ".csv":
            with open(f, encoding="utf-8-sig", newline="") as fh:
                lector = csv.DictReader(fh)
                campo = ("pregunta" if lector.fieldnames and "pregunta" in lector.fieldnames
                         else None)
                for fila in lector:
                    val = fila[campo] if campo else next(iter(fila.values()))
                    if val and val.strip():
                        preguntas.append(val.strip())
        elif f.suffix.lower() in (".txt", ".md", ""):   
            for linea in f.read_text(encoding="utf-8-sig").splitlines():
                linea = linea.strip()
                if linea and not linea.startswith("#") and linea.lower() != "pregunta":
                    preguntas.append(linea)
    return preguntas


cosenos = []
comunes_lista = []
for p in leer_preguntas(PREGUNTAS):
    v_fp32 = vectorizar(sesion_fp32, p)
    v_int8 = vectorizar(sesion_int8, p)

    cos = float(np.dot(v_fp32, v_int8) / (np.linalg.norm(v_fp32) * np.linalg.norm(v_int8)))

    top_fp32 = top_k(v_fp32)
    top_int8 = top_k(v_int8)


    comunes = len(set(top_fp32) & set(top_int8))
    print(f"  Trozos en común (de 5): {comunes}/5")
    cosenos.append(cos)
    comunes_lista.append(comunes)
    print(f"\nPregunta: {p}")
    print(f"  Paridad coseno fp32 vs int8: {cos:.5f}")


cosenos = np.array(cosenos)
comunes = np.array(comunes_lista)

print(f"\n--- ESTADÍSTICAS SOBRE {len(cosenos)} PREGUNTAS ---")
print(f"Paridad coseno media: {cosenos.mean():.4f}  (min {cosenos.min():.4f}, max {cosenos.max():.4f})")
print(f"Trozos en común de media: {comunes.mean():.2f} / 5")
print(f"Coincidencia media: {comunes.mean()/5*100:.1f}%")
print(f"Preguntas con 5/5: {(comunes==5).sum()}")
print(f"Preguntas con 4/5: {(comunes==4).sum()}")
print(f"Preguntas con 3/5: {(comunes==3).sum()}")


