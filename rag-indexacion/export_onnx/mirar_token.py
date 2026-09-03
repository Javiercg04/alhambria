import os, sys
import numpy as np

SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, SRC)

from indexado import tok

frase = "¿Dónde está la Torre de la Vela?"
salidas = tok.run(None, {tok.get_inputs()[0].name: np.array([frase])})

for i, s in enumerate(salidas):
    a = np.asarray(s)
    print(i, tok.get_outputs()[i].name, a.shape, a.reshape(-1)[:20])