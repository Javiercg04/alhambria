import sqlite3

# 1. Conéctate a tu archivo de base de datos
conexion = sqlite3.connect("../salida/indice/rag_v4.db")
cursor = conexion.cursor()

# 2. Ver qué tablas existen en tu base de datos
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()
print(f"Tablas encontradas: {tablas}")

# 3. Consultar los primeros 5 registros de una tabla
# Sustituye 'nombre_de_tu_tabla' por la tabla que te haya salido arriba
cursor.execute("SELECT * FROM chunks LIMIT 5;") 
filas = cursor.fetchall()

print("\n--- Muestra de los datos guardados ---")
for fila in filas:
    print(fila)

conexion.close()