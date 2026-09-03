from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

import os
import numpy as np
import onnxruntime as ort


MODELO = "BAAI/bge-m3"

CARPETA = os.path.join("..", "salida", "modelo")
RUTA_ONNX = os.path.join(CARPETA, "bge-m3.onnx")
RUTA_INT = os.path.join(CARPETA,"bge-m3.int8.onnx")

pregunta = "¿Quién mandó construir la Alhambra?"

modelo = SentenceTransformer(MODELO)
vec_ref = modelo.encode(pregunta, normalize_embeddings = True)

tokenizer = AutoTokenizer.from_pretrained(MODELO)
ort_session = ort.InferenceSession(RUTA_ONNX, providers=["CPUExecutionProvider"])

entradas = tokenizer(pregunta, return_tensors="np", padding=True, truncation=True, max_length=512)
vec_onnx = ort_session.run(["embedding"],{
    "input_ids": entradas["input_ids"].astype(np.int64),
    "attention_mask": entradas["attention_mask"].astype(np.int64)
})[0][0]

coseno = float(np.dot(vec_ref, vec_onnx) / (np.linalg.norm(vec_ref) * np.linalg.norm(vec_onnx)))
print("Paridad (coseno):", round(coseno, 6))
print("Referencia (5 primeros):", vec_ref[:5])
print("ONNX       (5 primeros):", vec_onnx[:5])

if coseno > 0.99: 
    print("PARIDAD CORRECTA")
else:
    print("PARIDAD INCORRECTA")


