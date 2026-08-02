import numpy as np
from pathlib import Path
import sqlite3
from sentence_transformers import SentenceTransformer
import requests
import csv
import sys

MODELO = "BAAI/bge-m3"
BASE = Path(__file__).parent
CONECTAR = BASE / ".." / "rag-indexacion" / "salida" / "indice" / "rag.db"
MODELO_LLM = "local-model"
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
PREGUNTAS = BASE / "preguntas_prueba"



ETIQUETA = "semantica_bge_m3_200"                      # identifica esta ejecucion
SALIDA_TXT = BASE / "salida" / f"resultados_{ETIQUETA}.txt"
SALIDA_CSV = BASE / "salida" / f"resultados_{ETIQUETA}.csv"
SALIDA_MD  = BASE / "salida" / f"detalle_{ETIQUETA}.md"
TOP_K = 5

sys.stdout.reconfigure(encoding="utf-8")

conexion = sqlite3.connect(CONECTAR)
filas = conexion.execute(
    "SELECT texto, embedding, fuente FROM chunks ORDER BY id").fetchall()
conexion.close()

textos  = [f[0] for f in filas]
datos   = np.stack([np.frombuffer(f[1], dtype=np.float32) for f in filas])
fuentes = [f[2] for f in filas]
print(f"Indice: {datos.shape[0]} chunks de {datos.shape[1]} dimensiones")

modelo = SentenceTransformer(MODELO)


def leer_preguntas(carpeta):
    if not carpeta.exists():
        raise SystemExit(f"No existe la carpeta {carpeta}")

    preguntas = []
    for f in sorted(carpeta.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() == ".csv":                 # CSV: usa cabecera
            with open(f, encoding="utf-8-sig", newline="") as fh:
                lector = csv.DictReader(fh)
                campo = ("pregunta" if lector.fieldnames and "pregunta" in lector.fieldnames
                         else None)
                for fila in lector:
                    val = fila[campo] if campo else next(iter(fila.values()))
                    if val and val.strip():
                        preguntas.append(val.strip())
        elif f.suffix.lower() in (".txt", ".md", ""):   # texto plano: una por linea
            for linea in f.read_text(encoding="utf-8-sig").splitlines():
                linea = linea.strip()
                if linea and not linea.startswith("#") and linea.lower() != "pregunta":
                    preguntas.append(linea)
    return preguntas


def responder(pregunta):    
    """Recupera el contexto y pide la respuesta al LLM.
    Devuelve (respuesta, posiciones_recuperadas, similitudes)."""
    vec = modelo.encode([pregunta], normalize_embeddings=True)[0].astype(np.float32)
    similitudes = datos @ vec
    mejores = [int(p) for p in np.argsort(similitudes)[::-1][:TOP_K]]

    contexto = ""
    for pos in mejores:
        contexto += f"[Fuente: {fuentes[pos]}]\n{textos[pos]}\n\n"

    payload = {
        "model": MODELO_LLM,
        "messages": [
            {"role": "system", "content":
                "Eres un experto en la Alhambra y respondes solo en espanol. "
                "Responde unicamente con la informacion del contexto. Si no esta "
                "en el contexto, di que no lo sabes. Si la pregunta no es sobre la "
                "Alhambra, di que no lo sabes."},
            {"role": "user", "content": f"Contexto:\n{contexto}\nPregunta: {pregunta}"},
        ],
        "temperature": 0.2,
    }
    r = requests.post(LM_STUDIO_URL, json=payload, timeout=300)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip(), mejores, similitudes


def parece_no_saber(respuesta):
    """Heuristica ORIENTATIVA para agilizar el triaje, no sustituye tu juicio."""
    marcas = ["no lo se", "no lo sé", "no se menciona", "no aparece", "no contiene",
              "no dispongo", "no se indica", "no se especifica", "no puedo responder"]
    r = respuesta.lower()
    return any(m in r for m in marcas)


preguntas = leer_preguntas(PREGUNTAS)
print(f"{len(preguntas)} preguntas encontradas en {PREGUNTAS}\n")

SALIDA_TXT.parent.mkdir(exist_ok=True)

# Reanudacion: si el CSV ya existe, cuenta lo hecho y continua
hechas = 0
if SALIDA_CSV.exists():
    with SALIDA_CSV.open(encoding="utf-8-sig", newline="") as fh:
        hechas = max(0, sum(1 for _ in csv.reader(fh, delimiter=";")) - 1)
    print(f"Retomando: {hechas} ya procesadas\n")

modo = "a" if hechas else "w"
fcsv = SALIDA_CSV.open(modo, encoding="utf-8-sig", newline="")
ftxt = SALIDA_TXT.open(modo, encoding="utf-8")
fmd  = SALIDA_MD.open(modo, encoding="utf-8")
escritor = csv.writer(fcsv, delimiter=";")

if not hechas:
    escritor.writerow(["n", "pregunta", "respuesta", "sim_max", "sim_min",
                       "fuentes", "dice_no_saber", "juicio", "tipo_fallo"])
    fmd.write(f"# Detalle de la evaluacion ({ETIQUETA})\n\n")

for i, pregunta in enumerate(preguntas[hechas:], start=hechas + 1):
    try:
        respuesta, mejores, sims = responder(pregunta)
    except requests.exceptions.ConnectionError:
        print("\nSin conexion con LM Studio. Progreso guardado; abrelo y relanza.")
        break
    except Exception as e:
        respuesta, mejores, sims = f"[error: {e}]", [], None

    if mejores:
        s_max, s_min = float(sims[mejores[0]]), float(sims[mejores[-1]])
        srcs = ", ".join(dict.fromkeys(fuentes[p] for p in mejores))
    else:
        s_max = s_min = 0.0
        srcs = ""

    escritor.writerow([i, pregunta, respuesta, f"{s_max:.4f}", f"{s_min:.4f}",
                       srcs, "si" if parece_no_saber(respuesta) else "no", "", ""])
    fcsv.flush()

    bloque = f"{i}. {pregunta}\n   -> {respuesta}"
    ftxt.write(bloque + "\n\n")
    ftxt.flush()

    fmd.write(f"## {i}. {pregunta}\n\n**Respuesta:** {respuesta}\n\n**Recuperado:**\n\n")
    for r_, pos in enumerate(mejores, 1):
        fmd.write(f"{r_}. `[{sims[pos]:.4f}]` ({fuentes[pos]}) "
                  f"{textos[pos][:300].replace(chr(10), ' ')}...\n\n")
    fmd.write("---\n\n")
    fmd.flush()

    print(f"[{i}/{len(preguntas)}] {s_max:.3f} | {pregunta[:60]}")

fcsv.close()
ftxt.close()
fmd.close()
print(f"\nTXT: {SALIDA_TXT}\nCSV: {SALIDA_CSV}\nMD : {SALIDA_MD}")