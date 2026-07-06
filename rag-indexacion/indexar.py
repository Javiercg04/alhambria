from sentence_transformers import SentenceTransformer
import numpy as np

modelo = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

#Corpus Ficticio
chunks = [
    "La Alhambra fue iniciada en el siglo XIII por Muhammad I ibn al-Ahmar, fundador de la dinastía nazarí.",
    "El Patio de los Leones corresponde al reinado de Muhammad V, en el siglo XIV.",
    "La Acequia Real abastecía de agua al conjunto, obra impulsada por Muhammad I.",
    "El Generalife era la finca de recreo de los sultanes nazaríes.",
]

vectores = modelo.encode(chunks, normalize_embeddings=True)

pregunta = "¿Quién mandó construir la Alhambra?"
vec_pregunta = modelo.encode([pregunta],normalize_embeddings=True)[0]

similitudes = vectores @ vec_pregunta
mejores = np.argsort(similitudes)[::-1][:2]

for i in mejores:
    print(f"{similitudes[i]:.3f}  {chunks[i]}")