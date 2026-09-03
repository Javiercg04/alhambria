from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
# Ajusta esta ruta a tu proyecto Android
ASSETS = Path(r"C:\Users\javie\OneDrive - UNIVERSIDAD DE GRANADA\Documentos\4Carrera\2 Cuatri\TFG\alhambria\app-android\app\src\main\assets")

FICHEROS = [
    BASE / "salida" / "indice" / "rag_v4.db",
    BASE / "salida" / "app" / "golden.json",
    BASE / "salida" / "modelo" / "tokenizer" / "tokenizer.onnx",
]

ASSETS.mkdir(parents=True, exist_ok=True)

for origen in FICHEROS:
    if not origen.exists():
        raise SystemExit(f"No existe {origen}")
    destino = ASSETS / origen.name
    shutil.copy2(origen, destino)
    print(f"{origen.name:<20} {destino.stat().st_size/1e6:>7.2f} MB")

print(f"\nCopiados en {ASSETS}")
print("Recuerda: si cambia el nombre de la base, actualiza nombreDB en LeerDB")
print("y añade el nombre anterior a la lista de obsoletas.")