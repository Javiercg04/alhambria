# extraccion.py

import fitz
from pathlib import Path
import re 


def extraer_texto(ruta):
    doc = fitz.open(ruta)
    return "\n".join(pagina.get_text() for pagina in doc)

def limpiar_texto(texto): 
    texto = re.sub(r'-\s*\n\s*', '',texto)   #"construc-\nción" -> "construcción
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    
    return texto.strip()


