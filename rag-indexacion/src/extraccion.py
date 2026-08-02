# extraccion.py

import fitz
from pathlib import Path
import re 

CABECERAS = [
    "JOSÉ MIGUEL PUERTA VÍLCHEZ",
    "LA ALHBAMBRA Y EL GENERALIFE DE GRANADA",
]

def extraer_texto(ruta):
    doc = fitz.open(ruta)
    flags = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE
    return "\n".join(pagina.get_text("text", flags=flags) for pagina in doc) 

def limpiar_texto(texto): 
    texto = re.sub(r'-\s*\n\s*', '',texto)  
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    return texto.strip()

def recortar_ruido(texto):
    corte = re.search(r'\n\s*(BIBLIOGRAF[IÍ]A|Bibliograf[ií]a|REFERENCIAS|Referencias|NOTAS)\s*\n',
                      texto)
    if corte:
        texto = texto[:corte.start()]

    for cab in CABECERAS:
        patron = r'\s*\d{0,4}\s*' + re.escape(cab) + r'\s*\d{0,4}\s*'
        texto = re.sub(patron, ' ', texto)

    texto = re.sub(r'.*I\.?S\.?S\.?N\.?.*\n', '', texto)

    texto = re.sub(r'Fig\.\s*\d+\..*?\n', '\n',texto)
    return texto 

def limpiar_texto_completo(texto):
    texto = recortar_ruido(texto)
    texto = limpiar_texto(texto)
    return texto 