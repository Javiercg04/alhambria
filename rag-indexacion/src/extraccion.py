# extraccion.py

import unicodedata

import fitz
from pathlib import Path
import re 

CABECERAS = [
    "JOSÉ MIGUEL PUERTA VÍLCHEZ",
    "LA ALHAMBRA Y EL GENERALIFE DE GRANADA",
]

MARCADORES = [
    r"Orientaci[oó]n bibliogr[aá]fica",
    r"BIBLIOGRAF[IÍ]A",
    r"Bibliograf[ií]a",
    r"REFERENCIAS",
    r"Referencias",
    r"\bReferences\b",
    r"\bNOTAS\b",
]

REEMPLAZOS = {
    "ˆ": "",            
    "‘": "'", "’": "'",
    "“": '"', "”": '"',
    "–": "-", "—": "-", 
    "…": "...",
    "ā": "a", "ī": "i", "ū": "u",
    "ḥ": "h", "ḍ": "d", "ṭ": "t", "ṣ": "s", "ẓ": "z",
    "ḏ": "d", "ġ": "g", "š": "sh", "ŷ": "y", "ĵ": "y",
    "à": "a", "á": "a", "â": "a", "ä": "a", "ã": "a", "å": "a",
    "è": "e", "é": "e", "ê": "e",
}


PROTEGIDAS = set("áéíóúüñÁÉÍÓÚÜÑ")

def extraer_texto(ruta):
    doc = fitz.open(ruta)
    flags = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE
    texto = "\n".join(pagina.get_text("text", flags=flags) for pagina in doc) 
    doc.close()
    return texto

def recortar_bibliografia(texto):
    patron = re.compile("(" + "|".join(MARCADORES) + ")")
    m = patron.search(texto)
    if m:
        texto = texto[:m.start()]
    return texto

def limpiar_texto(texto): 
    texto = re.sub(r'-\s*\n\s*', '',texto)  
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    return texto.strip()

def recortar_ruido(texto):
    texto = re.sub(r"Fig(?:ura)?\.?\s*\d+.*", " ", texto)

    texto = re.sub(r".*I\.?\s*S\.?\s*S\.?\s*N\.?.*", " ", texto)
    texto = re.sub(r"Artigrama,?\s*n[uú]m\.?\s*\d+.*", " ", texto)
   
    for cab in CABECERAS:
        patron = r'\s*\d{0,4}\s*' + re.escape(cab) + r'\s*\d{0,4}\s*'
        texto = re.sub(patron, ' ', texto)

    texto = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", texto)
    return texto 

def normalizar(texto):
    """Une palabras cortadas por guion, normaliza transcripcion y colapsa
    espacios. Conserva los acentos espanoles."""
 
    # Une palabras partidas a final de linea: "arqui-\ntectura" -> "arquitectura"
    texto = re.sub(r"-\s*\n\s*", "", texto)
 
    # Aplica el mapa de reemplazos de caracteres raros.
    for viejo, nuevo in REEMPLAZOS.items():
        texto = texto.replace(viejo, nuevo)
 
    # Quita marcas diacriticas residuales SIN tocar los acentos espanoles.
    salida = []
    for ch in texto:
        if ch in PROTEGIDAS:
            salida.append(ch)
            continue
        # descompone y elimina marcas combinantes (macrones, puntos, etc.)
        desc = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in desc if not unicodedata.combining(c))
        salida.append(base)
    texto = "".join(salida)
 
    # Deja solo caracteres utiles (letras, numeros, puntuacion basica).
    texto = re.sub(r'[^\w\s.,;:!?()\-"\'/]', " ", texto)
 
    # Colapsa todos los espacios/saltos en un solo espacio.
    texto = re.sub(r"\s+", " ", texto)
 
    return texto.strip()

def limpiar_texto_completo(texto):
    texto = recortar_bibliografia(texto)
    texto = recortar_ruido(texto)
    texto = normalizar(texto)
    return texto