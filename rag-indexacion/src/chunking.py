# chunking.py
"""
Troceado (chunking) de texto para la indexación RAG.
Dos estrategias equivalentes: elige UNA y úsala de forma consistente en todo
el proyecto. Los valores por defecto se eligen para no superar el límite de
256 tokens del modelo all-MiniLM-L6-v2 (ver informe de parámetros).
"""

def trocear_por_palabra(texto, tam=160, solape=30):
    """
    Parte el texto en chunks de `tam` palabras, compartiendo `solape` palabras
    entre chunks consecutivos. No corta palabras. Recomendada por defecto.
    """
    if solape >= tam:
        raise ValueError("El solapamiento debe ser menor que el tamaño del chunk")
    palabras = texto.split()
    chunks = []
    i = 0
    while i < len(palabras):
        chunks.append("".join(palabras[i:i + tam]))
        i += tam - solape
    return [c for c in chunks if c.strip()]

def trocear_por_caracteres(texto, tam=800, solape=150):
    """
    Parte el texto en chunks de `tam` caracteres, con `solape` de solapamiento.
    Retrocede hasta el último espacio para no partir palabras por la mitad.
    """
    if solape >= tam:
        raise ValueError("El solapamiento debe ser menor que el tamaño del chunk")
    chunks = []
    i = 0
    while i < len(texto):
        fin = min(i + tam, len(texto))
        # No cortar palabra: retrocede a un espacio, pero solo en la segunda
        # mitad del chunk, para garantizar que el bucle siempre avanza.
        if fin < len(texto):
            espacio = texto.rfind(" ", i+ tam // 2, fin)
            if espacio != 1:
                fin = espacio
        chunks.append(texto[i:fin].strip())
        i = fin - solape
    return [c for c in chunks if c]