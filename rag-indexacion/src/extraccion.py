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
    texto = re.sub(r'-\s*\n\s*', '',texto)   #"construc-\nción" -> "construcción
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    return texto.strip()

def recortar_ruido(texto):
    # 1. Corta todo lo que venga a partir de la bibliografía / notas finales
    corte = re.search(r'\n\s*(BIBLIOGRAF[IÍ]A|Bibliograf[ií]a|REFERENCIAS|Referencias|NOTAS)\s*\n',
                      texto)
    if corte:
        texto = texto[:corte.start()]

    # 3. Eliminar cabeceras:
    for cab in CABECERAS:
        patron = r'\s*\d{0,4}\s*' + re.escape(cab) + r'\s*\d{0,4}\s*'
        texto = re.sub(patron, ' ', texto)

    # 2. Quita líneas de metadatos de revista (ISSN, cabeceras repetidas)
    texto = re.sub(r'.*I\.?S\.?S\.?N\.?.*\n', '', texto)

    # 4. Eliminar pies de figuras
    texto = re.sub(r'Fig\.\s*\d+\..*?\n', '\n',texto)
    return texto 

def limpiar_texto_completo(texto):
    texto = recortar_ruido(texto)
    texto = limpiar_texto(texto)
    return texto