import numpy as np
import onnxruntime as ort
from onnxruntime_extensions import get_library_path
from transformers import AutoTokenizer
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RUTA_MODELO = BASE / "salida" / "modelo" / "bge-m3.int8.onnx"
RUTA_TOK = BASE / "salida" / "modelo" / "tokenizer" / "tokenizer.onnx"

PREGUNTAS = [
    "¿Quién mandó construir la Alhambra?",
    "¿Qué es el Patio de los Leones?",
    "¿Cuándo se fundó la dinastía nazarí?",
    "¿Dónde está la Torre de la Vela?",
    "¿Cuántas plantas tiene la Torre del Homenaje?",
]

emb = ort.InferenceSession(str(RUTA_MODELO), providers=["CPUExecutionProvider"])

# Camino A: tokenizador de HuggingFace (el que usa golden.py ahora)
hf = AutoTokenizer.from_pretrained("BAAI/bge-m3")

# Camino B: tokenizador ONNX (el que usará Android)
opts = ort.SessionOptions()
opts.register_custom_ops_library(get_library_path())
tok_onnx = ort.InferenceSession(str(RUTA_TOK), opts, providers=["CPUExecutionProvider"])
entrada_tok = tok_onnx.get_inputs()[0].name


def vector(ids):
    ids = np.asarray(ids, dtype=np.int64).reshape(1, -1)
    mask = np.ones_like(ids)
    salida = emb.run(None, {"input_ids": ids, "attention_mask": mask})[0]
    return np.asarray(salida).reshape(-1)


print(f"{'coseno':>10}  {'ids':>8}  pregunta")
print("-" * 70)

for p in PREGUNTAS:
    ids_hf = list(hf(p)["input_ids"])
    ids_on = np.asarray(tok_onnx.run(None, {entrada_tok: np.array([p])})[0]).reshape(-1).tolist()

    v_hf = vector(ids_hf)
    v_on = vector(ids_on)
    cos = float(np.dot(v_hf, v_on))

    print(f"{cos:>10.6f}  {'IGUAL' if ids_hf == ids_on else 'DISTINTO':>8}  {p}")

    if ids_hf != ids_on:
        print(f"            HF   ({len(ids_hf)}): {ids_hf}")
        print(f"            ONNX ({len(ids_on)}): {ids_on}")