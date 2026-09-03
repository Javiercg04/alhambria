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
# CORREGIDO: indexar.py escribe rag_v4.db, no rag.db.
RUTA_DB   = os.path.join(BASE, "..", "salida", "indice", "rag_v4.db")
PREGUNTAS = (BASE2 / ".." / ".." / "rag-consulta" / "preguntas_prueba").resolve()

K = 5

tokenizer = AutoTokenizer.from_pretrained(MODELO)
sesion_fp32 = ort.InferenceSession(RUTA_FP32, providers=["CPUExecutionProvider"])
sesion_int8 = ort.InferenceSession(RUTA_INT8, providers=["CPUExecutionProvider"])

# --- Cargar los textos del indice ---
conexion = sqlite3.connect(RUTA_DB)
filas = conexion.execute("SELECT id, texto, embedding, fuente FROM chunks ORDER BY id").fetchall()
conexion.close()

# CORREGIDO: antes ids = [f[0] ...] recogia el TEXTO, no el id, porque la
# consulta no pedia la columna id. Funcionaba de casualidad.
ids     = [f[0] for f in filas]
textos  = [f[1] for f in filas]
fuentes = [f[3] for f in filas]


def vectorizar(sesion, frases):
    e = tokenizer(frases, return_tensors="np", padding=True, truncation=True, max_length=512)
    return sesion.run(["embedding"], {
        "input_ids":      e["input_ids"].astype(np.int64),
        "attention_mask": e["attention_mask"].astype(np.int64),
    })[0]


def codificar_corpus(sesion, textos, lote=16):
    """Cada modelo codifica el corpus entero con sus propios pesos.

    Comparar int8 contra un indice generado en fp32 mezclaria dos espacios
    vectoriales distintos y la comparacion no seria justa.
    """
    trozos = []
    for i in range(0, len(textos), lote):
        trozos.append(vectorizar(sesion, textos[i:i + lote]))
        print(f"    {min(i + lote, len(textos))}/{len(textos)}", end="\r")
    m = np.vstack(trozos).astype(np.float32)
    return m / np.linalg.norm(m, axis=1, keepdims=True)


def top_k(matriz, vec, k=K):
    sims = matriz @ vec
    return np.argsort(sims)[::-1][:k]


def leer_preguntas(carpeta):
    """Devuelve lista de dicts {pregunta, fuente_correcta}.

    Si el CSV incluye una columna fuente_correcta, se puede medir el acierto
    real de cada modelo y no solo si ambos coinciden entre si.
    """
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
                        preguntas.append({
                            "pregunta": val.strip(),
                            "fuente_correcta": (fila.get("fuente_correcta") or "").strip() or None,
                        })
        elif f.suffix.lower() in (".txt", ".md", ""):   
            for linea in f.read_text(encoding="utf-8-sig").splitlines():
                linea = linea.strip()
                if linea and not linea.startswith("#") and linea.lower() != "pregunta":
                    preguntas.append({"pregunta": linea, "fuente_correcta": None})
    return preguntas


print("Codificando el corpus con fp32...")
indice_fp32 = codificar_corpus(sesion_fp32, textos)
print("\nCodificando el corpus con int8...")
indice_int8 = codificar_corpus(sesion_int8, textos)
print()

cosenos = []
comunes_lista = []
aciertos = {"fp32": 0, "int8": 0}
anotadas = 0

for item in leer_preguntas(PREGUNTAS):
    p = item["pregunta"]
    v_fp32 = vectorizar(sesion_fp32, [p])[0]
    v_int8 = vectorizar(sesion_int8, [p])[0]

    cos = float(np.dot(v_fp32, v_int8) / (np.linalg.norm(v_fp32) * np.linalg.norm(v_int8)))

    top_fp32 = top_k(indice_fp32, v_fp32)
    top_int8 = top_k(indice_int8, v_int8)

    comunes = len(set(top_fp32.tolist()) & set(top_int8.tolist()))
    cosenos.append(cos)
    comunes_lista.append(comunes)

    if item["fuente_correcta"]:
        anotadas += 1
        if item["fuente_correcta"] in {fuentes[i] for i in top_fp32}:
            aciertos["fp32"] += 1
        if item["fuente_correcta"] in {fuentes[i] for i in top_int8}:
            aciertos["int8"] += 1


cosenos = np.array(cosenos)
comunes = np.array(comunes_lista)

print(f"\n--- ESTADÍSTICAS SOBRE {len(cosenos)} PREGUNTAS ---")
print(f"Paridad coseno media: {cosenos.mean():.4f}  (min {cosenos.min():.4f}, max {cosenos.max():.4f})")
print(f"Trozos en común de media: {comunes.mean():.2f} / {K}")
print(f"Coincidencia media: {comunes.mean()/K*100:.1f}%")
print(f"Preguntas con {K}/{K}: {(comunes==K).sum()}")
print(f"Preguntas con {K-1}/{K}: {(comunes==K-1).sum()}")
print(f"Preguntas con {K-2}/{K}: {(comunes==K-2).sum()}")

if anotadas:
    print(f"\n--- ACIERTO REAL SOBRE {anotadas} PREGUNTAS ANOTADAS ---")
    for etiqueta in ("fp32", "int8"):
        print(f"Recall@{K} {etiqueta}: {aciertos[etiqueta]/anotadas*100:.1f} %")
else:
    print("\nSin columna fuente_correcta: solo se compara fp32 contra int8,")
    print("no se puede medir si aciertan.")