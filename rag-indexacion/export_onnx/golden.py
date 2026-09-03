import json, os, sys
import numpy as np

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)

from indexado import generar_embedding

preguntas = [
    "¿Quién mandó construir la Alhambra?",
    "¿Qué es el Patio de los Leones?",
    "¿Cuándo se fundó la dinastía nazarí?",
    "¿Dónde está la Torre de la Vela?",
    "¿Cuántas plantas tiene la Torre del Homenaje?",
]

vectores = generar_embedding(preguntas)

golden = [{"pregunta": p, "vector": [round(float(x), 6) for x in v]}
          for p, v in zip(preguntas, vectores)]

SALIDA = os.path.join(SRC, "..", "salida", "app")
os.makedirs(SALIDA, exist_ok=True)
ruta = os.path.join(SALIDA, "golden.json")

with open(ruta, "w", encoding="utf-8") as f:
    json.dump(golden, f, ensure_ascii=False)

print(f"golden.json con {len(golden)} preguntas en {os.path.abspath(ruta)}")
print(f"dimension: {vectores.shape[1]} | norma media: {np.linalg.norm(vectores, axis=1).mean():.6f}")