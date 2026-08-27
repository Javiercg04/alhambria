import json, os
import numpy as np, onnxruntime as ort
from transformers import AutoTokenizer

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_INT8 = os.path.join(BASE, "..", "salida", "modelo", "bge-m3.int8.onnx")

tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
ses_int8 = ort.InferenceSession(RUTA_INT8, providers=["CPUExecutionProvider"])

def emb(p):
    e = tok(p, return_tensors="np", padding=True, truncation=True, max_length=512)
    return ses_int8.run(["embedding"], {
        "input_ids": e["input_ids"].astype(np.int64),
        "attention_mask": e["attention_mask"].astype(np.int64),
    })[0][0]

preguntas = [
    "¿Quién mandó construir la Alhambra?",
    "¿Qué es el Patio de los Leones?",
    "¿Cuándo se fundó la dinastía nazarí?",
]
golden = [{"pregunta": p, "vector": emb(p).astype("float32").tolist()} for p in preguntas]

with open("golden.json", "w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False)
print("golden.json regenerado con el modelo int8:", len(golden), "preguntas")