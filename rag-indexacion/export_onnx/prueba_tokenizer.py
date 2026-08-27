
import numpy as np
import onnxruntime as ort
from onnxruntime_extensions import get_library_path
from transformers import AutoTokenizer
import os

MODELO = "BAAI/bge-m3"
CARPETA = os.path.join("..", "salida", "modelo", "tokenizer", "tokenizer.onnx")
RUTA_ONNX = os.path.join(CARPETA)

# Frases de prueba: incluye acentos, ñ y nombres propios (los casos delicados)
FRASES = [
    "¿Quién mandó construir la Alhambra?",
    "El Patio de los Leones es del siglo XIV.",
    "Muhammad I fundó la dinastía nazarí.",
    "La decoración nazarí combina yeserías y azulejos.",
]

tok = AutoTokenizer.from_pretrained(MODELO)
 
opciones = ort.SessionOptions()
opciones.register_custom_ops_library(get_library_path())
sesion = ort.InferenceSession(RUTA_ONNX, opciones)
nombre_entrada = sesion.get_inputs()[0].name
 
def ids_original(frase):
    return list(tok(frase)["input_ids"])
 
def ids_onnx(frase):
    salida = sesion.run(None, {nombre_entrada: np.array([frase])})
    return np.array(salida[0]).reshape(-1).astype(int).tolist()
 
total_tokens = 0
total_iguales = 0
frases_ok = 0
 
for frase in FRASES:
    a = ids_original(frase)
    b = ids_onnx(frase)
 
    # cuántas posiciones coinciden (comparando hasta la longitud menor)
    n = min(len(a), len(b))
    coinciden = sum(1 for i in range(n) if a[i] == b[i])
    igual_total = (a == b)
 
    total_tokens += max(len(a), len(b))
    total_iguales += coinciden
    if igual_total:
        frases_ok += 1
 
    print(f"\nFrase: {frase}")
    print(f"  original ({len(a)} ids): {a}")
    print(f"  onnx     ({len(b)} ids): {b}")
    print(f"  coinciden: {coinciden}/{max(len(a), len(b))}   "
          f"{'IDÉNTICO' if igual_total else 'DIFERENTE'}")
 
print("\n" + "=" * 60)
print(f"Frases idénticas:   {frases_ok}/{len(FRASES)}")
print(f"Tokens coincidentes: {total_iguales}/{total_tokens} "
      f"({100*total_iguales/total_tokens:.2f}%)")
print("El tokenizer.onnx es fiel al original."
      if frases_ok == len(FRASES) else
      "Hay diferencias: revisar la exportación.")