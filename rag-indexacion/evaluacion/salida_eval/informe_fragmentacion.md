# Evaluación intrínseca de fragmentación

Sin preguntas: se mide la calidad de los fragmentos en sí. Extracción y limpieza son idénticas entre estrategias; lo único que cambia es cómo se trocea. Los embeddings se calculan con el mismo modelo cuantizado que construye el índice.

## Corpus de partida

| Documento | Palabras | Frases | Palabras/frase |
|---|---:|---:|---:|
| martin_alcazaba_torre_homenaje | 10657 | 354 | 30.1 |
| N_22_08 | 12068 | 220 | 54.9 |
| **Total** | **22725** | **574** | **39.6** |

## Métricas por estrategia

| Estrategia | Nº chunks | Palabras (mín/med/máx) | Inicio limpio | Fin limpio | Cohesión intra | Huérfanos | Factor solape |
|---|---:|:--:|---:|---:|---:|---:|---:|
| A · por caracteres | 199 | 16/135/155 | 11% | 5% | 0.470 | 0 | 1.18 |
| B · por palabras | 198 | 77/135/135 | 10% | 4% | 0.476 | 0 | 1.17 |
| C · por frases | 168 | 105/135/231 | 100% | 100% | 0.510 | 0 | 1.00 |
| D · recursiva | 213 | 20/126/170 | 8% | 3% | 0.492 | 0 | 1.18 |
| E · semántica (elegida) | 170 | 41/134/231 | 100% | 100% | 0.529 | 0 | 1.00 |

### Reparto de fragmentos por documento

| Estrategia | martin_alcazaba_torre_homenaje | N_22_08 |
|---|---:|---:|
| A · por caracteres | 94 | 105 |
| B · por palabras | 93 | 105 |
| C · por frases | 86 | 82 |
| D · recursiva | 93 | 120 |
| E · semántica (elegida) | 88 | 82 |

**Cómo leer la tabla:**

- *Palabras*: mínimo, **media** y máximo por fragmento. En las estrategias de tamaño fijo el mínimo corresponde al último fragmento de cada documento, que recoge el texto sobrante y es más corto que el resto.
- *Inicio/fin limpio*: % de chunks que empiezan y terminan en un límite de frase. Mide si la estrategia respeta las frases.
- *Cohesión intra*: similitud coseno media entre todos los pares de frases de un mismo chunk, calculada con el modelo de embeddings del proyecto. Alta = el fragmento habla de una sola cosa. **No la maximices sola**: chunks minúsculos dan cohesión alta pero son inútiles; léela junto al tamaño.
- *Huérfanos*: chunks con menos de 15 palabras.
- *Factor de solape*: cuánto texto se contabiliza respecto al corpus original. 1,00 significa sin repetición. **Si dos estrategias tienen factores muy distintos, sus cifras no son comparables entre sí.**

## Filas para la tabla LaTeX

```latex
        Por caracteres             & 199 & 16/135/155        & 11\% & 5\% & 0.470 & 0 & 1.18 \\
        Por palabras               & 198 & 77/135/135        & 10\% & 4\% & 0.476 & 0 & 1.17 \\
        Por frases                 & 168 & 105/135/231        & 100\% & 100\% & 0.510 & 0 & 1.00 \\
        Recursiva                  & 213 & 20/126/170        & 8\% & 3\% & 0.492 & 0 & 1.18 \\
        Semántica (elegida)        & 170 & 41/134/231        & 100\% & 100\% & 0.529 & 0 & 1.00 \\
```

## Muestra de fragmentos

### A · por caracteres

1. (131 pal) El presente artículo, es un fragmento de la tesis doctoral: De la QASABAT al-QADiMA a la ALCAZABA ROJA , en la que se realiza un detallado estudio de la Alcazaba de la Alhambra, elaborado gracias a la recopilación y análisis de la diversa y amplia información existente sobre la misma. En este contexto abordamos una descripción del conjunto, y se elige la torre del Homenaje por ser un elemento clav […]

2. (129 pal) Gracias a la documentación gráfica existente y tras numerosas visitas a la Alcazaba; para comprobar y tomar medidas in situ, hemos redibujado la Alcazaba y sus elementos para ser más fieles a la realidad material existente y mostrar con claridad una de las mejores alcazabas hispanomusulmanas. Alhambra; Alcazaba; Torre del Homenaje; Construcción defensiva; Modelado 3D A NEW ARCHITECTURAL APPROACH T […]

3. (125 pal) en el mejor de los casos la tratan de forma meramente descriptiva, ocultando así el valor de una de las mejores alcazabas de España. Sólo algunos autores, como Manuel Gómez Moreno, Leopoldo Torres Balbás, Jesús Bermúdez Pareja y más recientemente Basilio Pavón Maldonado, Antonio Malpica Cuello y Carlos Vílchez Vílchez entre otros, han profundizado en el tema, dándole a la Alcazaba de la Alhambra l […]

### B · por palabras

1. (135 pal) El presente artículo, es un fragmento de la tesis doctoral: De la QASABAT al-QADiMA a la ALCAZABA ROJA , en la que se realiza un detallado estudio de la Alcazaba de la Alhambra, elaborado gracias a la recopilación y análisis de la diversa y amplia información existente sobre la misma. En este contexto abordamos una descripción del conjunto, y se elige la torre del Homenaje por ser un elemento clav […]

2. (135 pal) la documentación gráfica existente y tras numerosas visitas a la Alcazaba; para comprobar y tomar medidas in situ, hemos redibujado la Alcazaba y sus elementos para ser más fieles a la realidad material existente y mostrar con claridad una de las mejores alcazabas hispanomusulmanas. Alhambra; Alcazaba; Torre del Homenaje; Construcción defensiva; Modelado 3D A NEW ARCHITECTURAL APPROACH TO THE ALCA […]

3. (135 pal) descriptiva, ocultando así el valor de una de las mejores alcazabas de España. Sólo algunos autores, como Manuel Gómez Moreno, Leopoldo Torres Balbás, Jesús Bermúdez Pareja y más recientemente Basilio Pavón Maldonado, Antonio Malpica Cuello y Carlos Vílchez Vílchez entre otros, han profundizado en el tema, dándole a la Alcazaba de la Alhambra la importancia que se merece. La necesidad de realizar  […]

### C · por frases

1. (113 pal) El presente artículo, es un fragmento de la tesis doctoral: De la QASABAT al-QADiMA a la ALCAZABA ROJA , en la que se realiza un detallado estudio de la Alcazaba de la Alhambra, elaborado gracias a la recopilación y análisis de la diversa y amplia información existente sobre la misma. En este contexto abordamos una descripción del conjunto, y se elige la torre del Homenaje por ser un elemento clav […]

2. (130 pal) Gracias a la documentación gráfica existente y tras numerosas visitas a la Alcazaba; para comprobar y tomar medidas in situ, hemos redibujado la Alcazaba y sus elementos para ser más fieles a la realidad material existente y mostrar con claridad una de las mejores alcazabas hispanomusulmanas. Alhambra; Alcazaba; Torre del Homenaje; Construcción defensiva; Modelado 3D A NEW ARCHITECTURAL APPROACH T […]

3. (124 pal) Sólo algunos autores, como Manuel Gómez Moreno, Leopoldo Torres Balbás, Jesús Bermúdez Pareja y más recientemente Basilio Pavón Maldonado, Antonio Malpica Cuello y Carlos Vílchez Vílchez entre otros, han profundizado en el tema, dándole a la Alcazaba de la Alhambra la importancia que se merece. La necesidad de realizar una investigación exhaustiva sobre la Alcazaba de la Alhambra viene motivada po […]

### D · recursiva

1. (113 pal) El presente artículo, es un fragmento de la tesis doctoral: De la QASABAT al-QADiMA a la ALCAZABA ROJA , en la que se realiza un detallado estudio de la Alcazaba de la Alhambra, elaborado gracias a la recopilación y análisis de la diversa y amplia información existente sobre la misma. En este contexto abordamos una descripción del conjunto, y se elige la torre del Homenaje por ser un elemento clav […]

2. (109 pal) histórica y su caracterización arquitectónica, aportando inéditas planimetrías e infografías sobre la Alcazaba Gracias a la documentación gráfica existente y tras numerosas visitas a la Alcazaba; para comprobar y tomar medidas in situ, hemos redibujado la Alcazaba y sus elementos para ser más fieles a la realidad material existente y mostrar con claridad una de las mejores alcazabas hispanomusulma […]

3. (95 pal) centrado mayoritariamente en el estudio de sus palacios debido a su impresionante arquitectura y deslumbrante belleza Los trabajos y publicaciones dejan de lado la Alcazaba y en el mejor de los casos la tratan de forma meramente descriptiva, ocultando así el valor de una de las mejores alcazabas de España. Sólo algunos autores, como Manuel Gómez Moreno, Leopoldo Torres Balbás, Jesús Bermúdez Parej […]

### E · semántica (elegida)

1. (159 pal) El presente artículo, es un fragmento de la tesis doctoral: De la QASABAT al-QADiMA a la ALCAZABA ROJA , en la que se realiza un detallado estudio de la Alcazaba de la Alhambra, elaborado gracias a la recopilación y análisis de la diversa y amplia información existente sobre la misma. En este contexto abordamos una descripción del conjunto, y se elige la torre del Homenaje por ser un elemento clav […]

2. (129 pal) Alhambra; Alcazaba; Torre del Homenaje; Construcción defensiva; Modelado 3D A NEW ARCHITECTURAL APPROACH TO THE ALCAZABA AND THE TORRE DEL HOMENAJE I Los textos referentes a la ciudadela de la Alhambra siempre se han centrado mayoritariamente en el estudio de sus palacios debido a su impresionante arquitectura y deslumbrante belleza. Los trabajos y publicaciones dejan de lado la Alcazaba y en el m […]

3. (162 pal) La necesidad de realizar una investigación exhaustiva sobre la Alcazaba de la Alhambra viene motivada por dos razones fundamentales, la primera, por ser modelo de construcción defensiva, ejemplo de edificación militar para otras fortalezas hispanomusulmanas, y la segunda razón, citada anteriormente, por el hecho de ser una construcción que se encuentra tristemente a la sombra de los bellos palacio […]
