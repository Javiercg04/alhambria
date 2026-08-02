import json,os
from sentence_transformers import SentenceTransformer
import numpy as np, onnxruntime as ort
from transformers import AutoTokenizer

BASE = os.path.dirname(os.path.abspath(__file__))  
RUTA_FP32 = os.path.join(BASE, "..", "salida", "modelo", "bge-m3.onnx")
RUTA_INT8 = os.path.join(BASE, "..", "salida", "modelo", "bge-m3.int8.onnx")

modelo = SentenceTransformer("BAAI/bge-m3")
preguntas = [
    "¿Quién mandó construir la Alhambra?",
    "¿Qué es el Patio de los Leones?",
    "¿Cuándo se fundó la dinastía nazarí?",
]
golden = [
    {"pregunta": p, "vector": modelo.encode([p], normalize_embeddings=True)[0].astype("float32").tolist()}
    for p in preguntas
]
with open("golden.json", "w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False)
print("golden.json:", len(golden), "preguntas cortas")


tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
ses_fp32 = ort.InferenceSession(RUTA_FP32, providers=["CPUExecutionProvider"])
ses_int8 = ort.InferenceSession(RUTA_INT8, providers=["CPUExecutionProvider"])

def emb(ses, p):
    e = tok(p, return_tensors="np")
    return ses.run(["embedding"], {"input_ids": e["input_ids"].astype(np.int64),
                                    "attention_mask": e["attention_mask"].astype(np.int64)})[0][0]

p = "¿Qué es el Patio de los Leones?"
v32, v8 = emb(ses_fp32, p), emb(ses_int8, p)
print("coseno fp32 vs int8:", float(v32 @ v8 / (np.linalg.norm(v32)*np.linalg.norm(v8))))