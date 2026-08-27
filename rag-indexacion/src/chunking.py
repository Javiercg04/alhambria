# chunking.py
"""
Troceado (chunking) de texto para la indexación RAG.
Dos estrategias equivalentes: elige UNA y úsala de forma consistente en todo
el proyecto. Los valores por defecto se eligen para no superar el límite de
256 tokens del modelo all-MiniLM-L6-v2 (ver informe de parámetros).
"""
import re
import numpy as np


ABREVIATURAS = {
    "sr", "sra", "dr", "dra", "d", "dña", "ud", "uds", "prof", "profa",
    "pag", "pags", "pág", "págs", "vol", "vols", "num", "núm", "art", "arts",
    "cap", "caps", "fig", "figs", "ms", "mss", "p", "pp", "ej", "etc",
    "aprox", "g", "h", "r", "s", "n", "trad", "ed", "eds", "coord", "coords",
    "vid", "cf", "op", "loc", "cit", "ibid", "cfr",
}
 
def _dividir_en_frases(texto):
    patron = re.compile(r'([.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡«])')
    frases, pos = [], 0
    for m in patron.finditer(texto):
        fin_signo = m.end(1)
        antes = texto[:fin_signo - 1]
        match_palabra = re.search(r'(\w+)$', antes)
        palabra = match_palabra.group(1).lower() if match_palabra else ""
        # Solo se trata como abreviatura si HAY una palabra justo antes del
        # punto y esa palabra es corta/conocida. Si no hay palabra (el punto
        # va tras un paréntesis, comilla, número suelto, etc.), sí es fin de
        # frase real y hay que cortar.
        es_abreviatura_o_inicial = bool(palabra) and (len(palabra) <= 1 or palabra in ABREVIATURAS)
        if es_abreviatura_o_inicial:
            continue  # no es fin de frase real, seguimos acumulando
        frases.append(texto[pos:fin_signo].strip())
        pos = m.end()
    resto = texto[pos:].strip()
    if resto:
        frases.append(resto)
    return [f for f in frases if f]


def trocear_por_palabra(texto, tam=200, solape=30):
    if solape >= tam:
        raise ValueError("El solapamiento debe ser menor que el tamaño del chunk")
    palabras = texto.split()
    chunks = []
    i = 0
    while i < len(palabras):
        chunks.append(" ".join(palabras[i:i + tam]))
        i += tam - solape
    return [c for c in chunks if c.strip()]




def trocear_por_caracteres(texto, tam=1328, solape=199):
    if solape >= tam:
        raise ValueError("El solapamiento debe ser menor que el tamaño del chunk")
    chunks = []
    i = 0
    while i < len(texto):
        fin = min(i + tam, len(texto))
        if fin < len(texto):
            espacio = texto.rfind(" ", i+ tam // 2, fin)
            if espacio != -1 and espacio > 1:
                fin = espacio
        chunks.append(texto[i:fin].strip())
        nuevo_i = fin - solape
        if nuevo_i <= i:
            nuevo_i = fin

        if nuevo_i < len(texto) and texto[nuevo_i] != " ":
            siguiente_espacio = texto.find(" ", nuevo_i)
            if siguiente_espacio != -1:
                nuevo_i = siguiente_espacio + 1
        i = nuevo_i
    return [c for c in chunks if c]



def trocear_por_sentencias(texto, tam=200, solape_frases=2):
    frases = _dividir_en_frases(texto)
    chunks, actual, npal, hay_nuevo = [], [], 0, False
    for f in frases:
        actual.append(f)
        npal += len(f.split())
        hay_nuevo = True
        if npal >= tam:
            chunks.append(" ".join(actual))
            actual = actual[-solape_frases:] if solape_frases else []
            npal = sum(len(x.split()) for x in actual)
            hay_nuevo = False
    if actual and hay_nuevo:
        chunks.append(" ".join(actual))
    return chunks


def trocear_semantica(texto, embedding, percentil=75, tam_max=500):
    frases = _dividir_en_frases(texto)

    if len(frases) <= 1:
        return frases

    embeddings = embedding.encode(frases)

    def distancia_coseno(a, b):
        similitud = np.dot(a,b) / (np.linalg.norm(a) * np.linalg.norm(b))
        return 1 - similitud

    distancias = [
        distancia_coseno(embeddings[i], embeddings[i + 1])
        for i in range(len(embeddings) - 1)
    ]

    umbral = np.percentile(distancias, percentil)

    chunks = []
    actual = frases[0]

    for i, distancia in enumerate(distancias):
        candidata = actual + " " + frases[i + 1]
        if distancia > umbral or len(candidata) > tam_max:
            chunks.append(actual)
            actual = frases[i + 1]
        else:
            actual = candidata
    
    chunks.append(actual)
    return chunks

def trocear_recursiva(texto, tam=1328, solape=199, separadores=None):
    if separadores is None:
        separadores = ["\n\n", "\n", ". ", " ", ""]
    
    def dividir(texto, separadores):
        if len(texto) <= tam:
            return [texto]
        if not separadores: 
            return [texto[i:i + tam] for i in range(0, len(texto), tam)]
        
        sep, resto = separadores[0], separadores[1:]
        partes = texto.split(sep) if sep else list(texto)

        chunks, actual = [], ""
        for parte in partes:
            candidato = actual + (sep if actual else "") + parte
            if len(candidato) <= tam:
                actual = candidato
            else: 
                if actual:
                    chunks.append(actual)
                if len(parte) > tam:
                    chunks.extend(dividir(parte, resto))
                    actual = ""
                else:
                    actual = parte

        if actual:
            chunks.append(actual)
        return chunks
    
    chunks = dividir(texto, separadores)

    if solape > 0 and len(chunks) > 1:
        con_solape = [chunks[0]]
        for i in range(1, len(chunks)):
            anterior = chunks[i - 1]
            cola = anterior[-solape:]
            if len(cola) < len(anterior):
                primer_espacio = cola.find(" ")
                cola = cola[primer_espacio + 1:] if primer_espacio != -1 else ""
            separador = "" if (not cola or cola.endswith(" ") or chunks[i].startswith(" ")) else " "
            con_solape.append((cola + separador + chunks[i]) if cola else chunks[i]) 
        return con_solape
    
    return chunks

