# Evaluación intrínseca de fragmentación — N_22_08.pdf

Sin preguntas: se mide la calidad de los fragmentos en sí. Extracción y limpieza son idénticas entre estrategias (tu código de src); lo único que cambia es cómo se trocea.

## Métricas por estrategia

| Estrategia | Nº chunks | Palabras (mín/med/máx) | Inicio limpio | Fin limpio | Cohesión intra (muestra) | Huérfanos |
|---|---:|:--:|---:|---:|---:|---:|
| A · por caracteres | 77 | 30/222/249 | 16% | 12% | 0.490 | 0 |
| B · por palabras (actual) | 84 | 70/200/200 | 14% | 4% | 0.486 | 0 |
| C · por frases | 130 | 200/244/380 | 100% | 100% | 0.515 | 0 |
| D · por tamaño respetando frases | 75 | 146/226/261 | 12% | 1% | 0.501 | 0 |
| E · semántico | 114 | 4/143/231 | 100% | 100% | 0.564 | 5 |

**Cómo leer la tabla:**

- *Inicio/fin limpio*: % de chunks que empiezan y terminan en un límite de frase. Mide si la estrategia respeta las frases. Por caracteres sale bajo; por frases, cerca del 100%.
- *Cohesión intra*: cómo de parecidas son entre sí las frases de un mismo chunk. Alta = habla de una sola cosa. **No la maximices sola**: chunks minúsculos dan cohesión alta pero son inútiles; léela junto al tamaño.
- *Huérfanos*: chunks con menos de 15 palabras.

> La mejor fragmentación combina a la vez cortes limpios, cohesión razonable y tamaño útil sin huérfanos. La tabla orienta; la muestra decide.

## Muestra de fragmentos (léelos y juzga si cada uno es una idea completa)

### A · por caracteres

1. (195 pal) La Alhambra y el Generalife de Granada  Resumen Se ofrece aquí una síntesis sobre el conjunto monumental de la Alhambra y el Generalife atendiendo a su evolución histórica y a sus principales características constructivas, decorativas y simbólicas, a partir de las aportaciones de la tradicional y reciente historiografía, y prestando especial atención a los textos árabes nazaríes y a los nuevos dat […]

2. (220 pal) Ibn al-Ahmar, conlleva el desarrollo de una nueva y postrera actividad edilicia islámica en el reducido territorio de al-Andalus, que brillará con luz propia hasta la actualidad por haber creado el excepcional conjunto monumental de la Alhambra y el Generalife, síntesis y culminación de la gran arquitectura andalusí, hoy Patrimonio de la Humanidad y uno de los sitios con mayor poder de atracción s […]

3. (221 pal) la irrigó abriendo una acequia con caudal propio y, en menos de un año, estaban listas sus murallas, según el ms. anónimo de Madrid y Copenhague. El lugar elegido, la parte más occidental de la colina, tenía ya denominación y cierto pasado arquitectónico castrense, por cuanto que las crónicas árabes se refieren a una Qalat (fortaleza), Maqil (refugio) o Hisn (castillo), llamada siempre al-Hamra (L […]

4. (226 pal) del lugar con consecuencias de mucho mayor alcance (fig. 1). El nuevo soberano nazarí, cuyo apellido familiar, al-Ahmar (el Rojo), venía a coincidir con la denominación que ya tenía el lugar y, asimismo, con el topónimo de Granada, de origen latino y vinculado a la fruta de la granada y a su color, nació precisamente en 1195, el año de Alarcos, como dice Ibn al-Jatib, y tomó para su nueva dinastía […]

### B · por palabras (actual)

1. (200 pal) La Alhambra y el Generalife de Granada Resumen Se ofrece aquí una síntesis sobre el conjunto monumental de la Alhambra y el Generalife atendiendo a su evolución histórica y a sus principales características constructivas, decorativas y simbólicas, a partir de las aportaciones de la tradicional y reciente historiografía, y prestando especial atención a los textos árabes nazaríes y a los nuevos dato […]

2. (200 pal) una nueva y postrera actividad edilicia islámica en el reducido territorio de al-Andalus, que brillará con luz propia hasta la actualidad por haber creado el excepcional conjunto monumental de la Alhambra y el Generalife, síntesis y culminación de la gran arquitectura andalusí, hoy Patrimonio de la Humanidad y uno de los sitios con mayor poder de atracción sobre multitud de personas de todas las g […]

3. (200 pal) la nueva fortaleza, puso a quien dirigiese las obras, la irrigó abriendo una acequia con caudal propio y, en menos de un año, estaban listas sus murallas, según el ms. anónimo de Madrid y Copenhague. El lugar elegido, la parte más occidental de la colina, tenía ya denominación y cierto pasado arquitectónico castrense, por cuanto que las crónicas árabes se refieren a una Qalat (fortaleza), Maqil (r […]

4. (200 pal) Los almohades, en fin, volverán a utilizar la entonces también llamada al-Qasaba al-Hamra (Alcazaba Roja), hasta que con la llegada de Muhammad I se inicia una verdadera refundación del lugar con consecuencias de mucho mayor alcance (fig. 1). El nuevo soberano nazarí, cuyo apellido familiar, al-Ahmar (el Rojo), venía a coincidir con la denominación que ya tenía el lugar y, asimismo, con el topónim […]

### C · por frases

1. (235 pal) La Alhambra y el Generalife de Granada  Resumen Se ofrece aquí una síntesis sobre el conjunto monumental de la Alhambra y el Generalife atendiendo a su evolución histórica y a sus principales características constructivas, decorativas y simbólicas, a partir de las aportaciones de la tradicional y reciente historiografía, y prestando especial atención a los textos árabes nazaríes y a los nuevos dat […]

2. (209 pal) The article takes the contributions of traditional and recent historiography as a starting point, paying special attention to Nasrid Arabic texts and the new toponymical, historical, poetic and functional data recently arisen about some important spaces of the Alhambra. El derrumbamiento del estado almohade y la subsecuente creación del reino nazarí de Granada por parte de Muhammad b. Yusuf b. Nas […]

3. (233 pal) El derrumbamiento del estado almohade y la subsecuente creación del reino nazarí de Granada por parte de Muhammad b. Yusuf b. Nasr Ibn al-Ahmar, conlleva el desarrollo de una nueva y postrera actividad edilicia islámica en el reducido territorio de al-Andalus, que brillará con luz propia hasta la actualidad por haber creado el excepcional conjunto monumental de la Alhambra y el Generalife, síntesi […]

4. (209 pal) La fortaleza roja Muhammad I (g. 1232-1273), perteneciente a una noble familia de origen árabe establecida en Arjona, se proclamó sultán en esta ciudad jiennense en 1232 y, tras declararse vasallo de Fernando III de Castilla, entró pacíficamente en Granada el mes de mayo de 1238 y se instaló en el palacio zirí del siglo XI de la Alcazaba Qadima (Antigua), en la parte  Profesor Titular de la Univer […]

### D · por tamaño respetando frases

1. (163 pal) La Alhambra y el Generalife de Granada  Resumen Se ofrece aquí una síntesis sobre el conjunto monumental de la Alhambra y el Generalife atendiendo a su evolución histórica y a sus principales características constructivas, decorativas y simbólicas, a partir de las aportaciones de la tradicional y reciente historiografía, y prestando especial atención a los textos árabes nazaríes y a los nuevos dat […]

2. (243 pal) data recently arisen about some important spaces of the Alhambra.      El derrumbamiento del estado almohade y la subsecuente creación del reino nazarí de Granada por parte de Muhammad b. Yusuf b Nasr Ibn al-Ahmar, conlleva el desarrollo de una nueva y postrera actividad edilicia islámica en el reducido territorio de al-Andalus, que brillará con luz propia hasta la actualidad por haber creado el e […]

3. (208 pal) la nueva fortaleza, puso a quien dirigiese las obras, la irrigó abriendo una acequia con caudal propio y, en menos de un año, estaban listas sus murallas, según el ms. anónimo de Madrid y Copenhague El lugar elegido, la parte más occidental de la colina, tenía ya denominación y cierto pasado arquitectónico castrense, por cuanto que las crónicas árabes se refieren a una Qalat (fortaleza), Maqil (re […]

4. (254 pal) la entonces también llamada al-Qasaba al-Hamra (Alcazaba Roja), hasta que con la llegada de Muhammad I se inicia una verdadera refundación del lugar con consecuencias de mucho mayor alcance (fig. 1) El nuevo soberano nazarí, cuyo apellido familiar, al-Ahmar (el Rojo), venía a coincidir con la denominación que ya tenía el lugar y, asimismo, con el topónimo de Granada, de origen latino y vinculado a […]

### E · semántico

1. (142 pal) La Alhambra y el Generalife de Granada  Resumen Se ofrece aquí una síntesis sobre el conjunto monumental de la Alhambra y el Generalife atendiendo a su evolución histórica y a sus principales características constructivas, decorativas y simbólicas, a partir de las aportaciones de la tradicional y reciente historiografía, y prestando especial atención a los textos árabes nazaríes y a los nuevos dat […]

2. (170 pal) El derrumbamiento del estado almohade y la subsecuente creación del reino nazarí de Granada por parte de Muhammad b. Yusuf b. Nasr Ibn al-Ahmar, conlleva el desarrollo de una nueva y postrera actividad edilicia islámica en el reducido territorio de al-Andalus, que brillará con luz propia hasta la actualidad por haber creado el excepcional conjunto monumental de la Alhambra y el Generalife, síntesi […]

3. (198 pal) Muy poco después ordenó erigir una nueva sede monárquica sobre la colina de la Sabika (lingote), en el sitio llamado al-Hamra (la Roja), donde marcó los cimientos de la nueva fortaleza, puso a quien dirigiese las obras, la irrigó abriendo una acequia con caudal propio y, en menos de un año, estaban listas sus murallas, según el ms. anónimo de Madrid y Copenhague. El lugar elegido, la parte más occ […]

4. (154 pal) Los almohades, en fin, volverán a utilizar la entonces también llamada al-Qasaba al-Hamra (Alcazaba Roja), hasta que con la llegada de Muhammad I se inicia una verdadera refundación del lugar con consecuencias de mucho mayor alcance (fig. 1). El nuevo soberano nazarí, cuyo apellido familiar, al-Ahmar (el Rojo), venía a coincidir con la denominación que ya tenía el lugar y, asimismo, con el topónim […]
