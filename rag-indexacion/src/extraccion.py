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
    # Acento grave, circunflejo y dieresis extranjeros: si se normalizan.
    "à": "a", "â": "a", "ä": "a", "ã": "a", "å": "a",
    "è": "e", "ê": "e", "ë": "e",
    "ì": "i", "î": "i", "ï": "i",
    "ò": "o", "ô": "o", "õ": "o",
    "ù": "u", "û": "u",
    "ç": "c",
}

MIN_PT = 8.0
ZONA_BIBLIOGRAFIA = 0.5

PROTEGIDAS = set("áéíóúüñÁÉÍÓÚÜÑ")

def extraer_texto(ruta, min_pt = MIN_PT):
    doc = fitz.open(ruta)

    if not min_pt: 
        flags = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE
        texto = "\n".join(pagina.get_text("text", flags=flags) for pagina in doc) 
        doc.close()
        return texto

    lineas = []
    for pagina in doc:
        for bloque in pagina.get_text("dict")["blocks"]:
            for linea in bloque.get("lines",[]):
                contenido = "".join(s["text"] for s in linea["spans"]
                                    if s["size"] >= min_pt)
                if contenido.strip():
                    lineas.append(contenido)

    doc.close()
    return "\n".join(lineas)

def recortar_bibliografia(texto, verbose=False):
    inicio = int(len(texto) * ZONA_BIBLIOGRAFIA)
    patron = re.compile("(" + "|".join(MARCADORES) + ")")

    ultimo = None
    for m in patron.finditer(texto, inicio):
        ultimo = m

    if ultimo is None:
        return texto

    return texto[: ultimo.start()]


def limpiar_texto(texto):
    texto = re.sub(r'-\s*\n\s*', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    return texto.strip()

def recortar_ruido(texto):
    texto = re.sub(r"Fig(?:ura)?\.?\s*\d+.*", " ", texto)
    texto = re.sub(r".*I\.?\s*S\.?\s*S\.?\s*N\.?.*", " ", texto)
    texto = re.sub(r"Artigrama,?\s*n[uú]m\.?\s*\d+.*", " ", texto)
    texto = re.sub(r"Foto:\s*[^.]*\(Edilux\)\.?", " ", texto)
    texto = re.sub(r"(?i)CUADERNOS DE LA ALHAMBRA\s*\|[^\n]*", " ", texto)
    texto = re.sub(r"(?:Artículos|En la Alhambra|Homenaje)\s*•[^\n]*", " ", texto)
    
    texto = re.sub(r"ABSTRACT.*?(?=CÓMO CITAR|$)", " ", texto, flags=re.S)
    texto = re.sub(r"KEY WORDS[^\n]*", " ", texto)
    texto = re.sub(r"CÓMO CITAR / HOW TO CITE.*?ISSN[^\n]*", " ", texto, flags=re.S)

    
    texto = re.sub(r"(?:[A-ZÁÉÍÓÚÑ]\s){4,}[A-ZÁÉÍÓÚÑ]", " ", texto)
    texto = re.sub(
    r"The following article.*?(?=A NEW ARCHITECTURAL|Los textos referentes|$)",
    " ", texto, flags=re.S
        )
   
    for cab in CABECERAS:
        patron = r'\s*\d{0,4}\s*' + re.escape(cab) + r'\s*\d{0,4}\s*'
        texto = re.sub(patron, ' ', texto)

    texto = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", texto)
    return texto 

def normalizar(texto):
    texto = re.sub("\u00ad\\s*\n?\\s*", "", texto)
    texto = re.sub(r"-\s*\n\s*", "", texto)
    texto = re.sub(r"\n([A-ZÁÉÍÓÚÑ])\n(?=[a-záéíóúñ])", r"\n\1", texto)
    for viejo, nuevo in REEMPLAZOS.items():
        texto = texto.replace(viejo, nuevo)
 
    
    salida = []
    for ch in texto:
        if ch in PROTEGIDAS:
            salida.append(ch)
            continue
        desc = unicodedata.normalize("NFKD", ch)
        base = "".join(c for c in desc if not unicodedata.combining(c))
        salida.append(base)
    texto = "".join(salida)
    
    texto = re.sub(r'[^\w\s.,;:!?()\-"\'/]', " ", texto)
 
    texto = re.sub(r"\s+", " ", texto)
 
    return texto.strip()

def limpiar_texto_completo(texto):
    texto = recortar_bibliografia(texto)
    texto = recortar_ruido(texto)
    texto = normalizar(texto)
    return texto