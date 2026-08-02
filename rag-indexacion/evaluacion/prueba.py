import fitz
import re

ruta = "../corpus/N_22_08.pdf"

def extraer_texto(ruta):
    doc = fitz.open(ruta)
    flags = fitz.TEXT_PRESERVE_LIGATURES | fitz.TEXT_PRESERVE_WHITESPACE
    return "\n".join(pagina.get_text("text", flags=flags) for pagina in doc) 

texto = extraer_texto(ruta)

def limpiar_texto(texto): 
    texto = re.sub(r'-\s*\n\s*', '',texto)   #"construc-\nción" -> "construcción
    texto = re.sub(r'\s+', ' ', texto)
    texto = re.sub(r'[^\w\s.,;:!?()\-"]', '', texto)
    return texto

texto_limpio = limpiar_texto(texto)

print(repr(texto_limpio[:120]))