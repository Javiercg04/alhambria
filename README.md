# AlhambrIA

Asistente conversacional sobre el patrimonio de la Alhambra que funciona íntegramente en el dispositivo, sin conexión a internet.

La aplicación implementa un sistema RAG (*Retrieval-Augmented Generation*) sobre Android: recupera fragmentos de un corpus documental almacenado en el teléfono y los entrega a un modelo de lenguaje pequeño que genera la respuesta. Todo el proceso ocurre en local. La única conexión necesaria es la del primer arranque, para descargar los dos modelos.

Trabajo de Fin de Grado. La memoria completa documenta las decisiones de diseño y los experimentos que las respaldan.

---

## Cómo funciona

El proyecto explora dos vías. La primera, el ajuste fino de un modelo sobre el dominio, se descartó por las limitaciones de hardware. La segunda, el RAG, es la que se implementa.

**Fase de indexación** (una vez, en el ordenador)

El corpus se extrae de los PDF originales, se limpia y se fragmenta por cambios de temática. Cada fragmento se vectoriza con `bge-m3`, exportado a ONNX y cuantizado a 8 bits, y se almacena en una base SQLite como `BLOB`.

**Fase de consulta** (en el dispositivo)

La pregunta del usuario se vectoriza con el mismo modelo, se comparan los vectores por similitud coseno y se recuperan los cinco fragmentos más próximos. Ese contexto se entrega al modelo de lenguaje, que ejecuta sobre LiteRT-LM.

## Decisiones principales

| Componente | Elección | Motivo |
|---|---|---|
| Fragmentación | Semántica | Única junto a la de frases que respeta los límites de oración, y con mayor cohesión interna |
| Embedding | `bge-m3` (int8) | Multilingüe y el mejor de los tres evaluados; cuantizado de 2,27 GB a 555 MB |
| Índice | SQLite + `BLOB` | Nativo en Android, sin dependencias externas; el corpus es estático y pequeño |
| Recuperación | Semántica, k=5 | La componente léxica solo mejoraría el orden, y el sistema no pondera por posición |
| Motor de inferencia | LiteRT-LM | Mejor integración en Android que llama.cpp o ExecuTorch |
| Modelo de lenguaje | Qwen3-0.6B | Doble tasa de acierto que Gemma3-1B, y sus fallos son visibles en lugar de inventados |

## Resultados

Medido sobre un Redmi Note 11 (6 GB de RAM, Snapdragon 680, sin NPU):

- El fragmento correcto entra entre los cinco recuperados en el **88,9 %** de los casos.
- Tras el truncado que impone la memoria del dispositivo, el dato sigue presente en el **80 %**.
- La respuesta final es correcta en el **60 %**.

El cuello de botella no está en la recuperación, sino en la capacidad de un modelo de esta escala para razonar sobre el texto que recibe.

---

## Estructura

```
alhambria/
├── finetuning/          # vía descartada (capítulo 4 de la memoria)
├── rag-indexacion/      # generación de los artefactos
│   ├── export_onnx/
│   └── indexar.py
└── app-android/             # la aplicación
```

## Orden de ejecución

Los pasos deben seguirse en orden. La fragmentación y la indexación emplean el modelo de embedding ya exportado y cuantizado, así que los tres primeros pasos van antes que el cuarto. Construir el índice con el modelo original y consultarlo después con el cuantizado situaría ambos conjuntos en espacios vectoriales distintos y degradaría la recuperación.

**0. Obtener el proyecto**

```bash
git clone https://github.com/Javiercg04/alhambria.git
cd alhambria
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**1. Exportar el modelo de embedding** → `salida/modelo/bge-m3.onnx` y `bge-m3.onnx.data`

```bash
python rag-indexacion/export_onnx/exportar.py
```

**2. Cuantizar el modelo** → `salida/modelo/bge-m3.int8.onnx`

```bash
python rag-indexacion/export_onnx/cuantizar.py
```

**3. Exportar el tokenizador** → `salida/modelo/tokenizer/tokenizer.onnx`

```bash
python rag-indexacion/export_onnx/exportar_tokenizer.py
```

**4. Construir el índice** → `salida/indice/rag_vX.db`

Extrae, limpia, fragmenta e indexa el corpus.

```bash
python rag-indexacion/indexar.py
```

**5. Desplegar los artefactos** → `android/app/src/main/assets/`

Copia el índice, el tokenizador y el fichero de referencia.

```bash
python rag-indexacion/desplegar_assets.py
```

**6. Compilar la aplicación** → `android/app/build/outputs/apk/debug/`

```bash
cd android
./gradlew assembleDebug            # Windows: gradlew.bat assembleDebug
```

---

## Los modelos no están en el repositorio

Ni el modelo de embedding cuantizado (555 MB) ni el modelo de lenguaje (497 MB) se versionan ni se empaquetan en el APK. La aplicación los descarga en el primer arranque desde las direcciones declaradas en `ModelProvider`. A partir de ese momento funciona sin conexión.

Para cambiar el modelo de lenguaje basta con modificar la URL de `ensureLlmModel`.

## Corpus

El sistema se construye sobre dos fuentes:

- *La Alhambra y el Generalife de Granada*, J. M. Puerta Vílchez
- *La Alcazaba y la Torre del Homenaje bajo una nueva mirada arquitectónica*, A. Martín Martín

Los PDF no se incluyen en el repositorio por razones de licencia.
