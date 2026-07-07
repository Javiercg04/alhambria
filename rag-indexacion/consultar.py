import numpy as np
from pathlib import Path
import sqlite3
from sentence_transformers import SentenceTransformer
import requests
import json

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
BASE = Path(__file__).parent
DATOS = BASE / "salida" / "vectores.npy"
CONECTAR = BASE / "salida" / "rag.db"
MODELO_LLM = "gemma-3-4b-it"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"



datos = np.load(DATOS)

conexion = sqlite3.connect(CONECTAR)
cursor = conexion.cursor()

modelo = SentenceTransformer(MODELO)
pregunta = f""" 1. Las limitaciones de los registros históricos del siglo XIX
Durante siglos, el estudio de los mocárabes de la Alhambra arrastró ciertas imprecisiones debido a las limitaciones técnicas de las épocas en las que se intentaron documentar por primera vez:

Owen Jones y Jules Goury (1842): Aunque fueron pioneros al proponer una "gramática elemental" (un sistema que combinaba figuras geométricas básicas como triángulos y rectángulos para formar las piezas), asumieron de forma teórica que ambos pabellones eran simétricos e idénticos. Hoy sabemos que solo dibujaron el pabellón occidental y dieron por hecho que el oriental era un reflejo exacto, lo cual era falso.

Nicomedes de Mendívil (1859-1862): Realizó unos planos de una calidad y un sombreado espectaculares, pero cometió el error de no especificar a cuál de los dos pabellones correspondían sus dibujos. Además, asumiendo una simetría perfecta, dejó a la mitad el diseño de dos de las arcadas. El análisis actual ha podido comprobar que el pabellón que Mendívil dibujó en secreto fue el occidental.

2. Las tres fases del análisis moderno (Metodología)
Para superar los vacíos del pasado, el estudio actual implementó una estrategia en tres fases consecutivas que combina historia y tecnología punta:

Fase 1: Evolución e hitos históricos. Se recopilaron y cruzaron grabados, pinturas y fotografías antiguas (desde el siglo XVII hasta el XX). Esto permitió reconstruir cómo afectaron a los pabellones grandes catástrofes —como la brutal explosión de un molino de pólvora cercano en 1590— y evaluar el impacto de restauraciones polémicas, como la realizada por Rafael Contreras en 1859, quien sustituyó el tejado del pabellón oriental por una cúpula de cerámica que acabó provocando filtraciones de agua.

Fase 2: Modelado geométrico digital (CAD). Por primera vez se levantaron planos informáticos individualizados de cada grupo de mocárabes. Al aplicarles un código de colores según su tipología geométrica, se pudieron poner a prueba los tratados de carpintería histórica y descubrir los patrones matemáticos teóricos que intentaron seguir los maestros nazaríes.

Fase 3: Escaneo láser 3D de alta precisión. Se utilizó un escáner tridimensional en el propio Patio de los Leones para capturar millones de puntos que reflejan el estado real y milimétrico de las estructuras. Mediante programas de gestión tridimensional, se aislaron los pabellones y se extrajeron secciones y alzados exactos que habrían sido imposibles de medir de forma manual debido a la altura y la extrema complejidad de los relieves.

3. Descubrimientos e implicaciones inéditas
Al contrastar los modelos teóricos de ordenador con la cruda realidad física capturada por el láser, salieron a la luz tres hallazgos cruciales:

El recuento real de piezas: Se desmintió definitivamente el mito de que los dos pabellones son iguales. El pabellón occidental está compuesto por un total de 2258 piezas de mocárabes, mientras que el pabellón oriental tiene 2222 piezas. Sus arcadas y la distribución de sus pechinas son completamente distintas.

Deformaciones originales por intuición artesanal: El análisis demostró que los constructores del siglo XIV no pudieron limitarse a aplicar matemáticas puras. Para resolver el complejo reto arquitectónico de pasar de una base cuadrada (las pechinas) a una cúpula superior circular, los artesanos se vieron obligados a tallar de manera intuitiva piezas deformadas ad-hoc. Estas piezas especiales "absorbían" el error geométrico para evitar que los mocárabes se solaparan o dejaran huecos vacíos.

Deformaciones estructurales por el paso del tiempo: El escáner láser desveló que las plantas de los pabellones no forman cuadrados perfectos, sino que están inclinadas y estiradas entre 10 y 13 centímetros hacia el centro del patio, llegando a registrar desplomes de hasta 4 grados en sus columnas. Estas deformaciones son la cicatriz material de siglos de terremotos, explosiones y sutiles movimientos del subsuelo. En lugar de colapsar, la flexibilidad del sistema de mocárabes y las reparaciones históricas (donde simplemente se rellenaban las grietas asentando la deformación) permitieron que estas delicadas estructuras sobrevivieran hasta nuestros días."
"""
vec_pregunta = modelo.encode([pregunta], normalize_embeddings=True)[0]
contexto = ""


similitudes = datos @ vec_pregunta
for pos in np.argsort(similitudes)[::-1][:10]:
    pos = int(pos)
    texto = cursor.execute("SELECT texto FROM chunks WHERE id = ?", (pos,)).fetchone()[0]
    print(f"[{similitudes[pos]:.3f}] (pos {pos}) {texto[:120]}")

    if texto: 
        contexto += texto + "\n\n"

prompt = f"""
Eres experto en la Alhambra y solo puedes responder en español. Si no sabes la respuesta debes decir que no lo sabes. Si es otro tema distinto a la Alhambra tampoco lo sabes.

Contexto: {contexto}

Pregunta: {pregunta}

"""

payload = {
    "model": "gemma-3-4b-it",
    "messages": [
        {
            "role": "system",
            "content": (
                "Eres un experto en la Alhambra. "
                "Responde únicamente usando el contexto proporcionado. "
                "Si el contexto no contiene la respuesta, di que no lo sabes."
            )
        },
        {
            "role": "user",
            "content": f"Contexto:\n{contexto}\n\nPregunta:\n{pregunta}"
        }
    ],
    "temperature": 0.2
}

r = requests.post(LM_STUDIO_URL, json=payload)

print(r.json()["choices"][0]["message"]["content"])


conexion.close()

