from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModel

import torch, os, onnx, glob
import numpy as np
import onnxruntime as ort

CARPETA = os.path.join("..", "salida", "modelo")
os.makedirs(CARPETA, exist_ok=True)
RUTA_ONNX = os.path.join(CARPETA, "bge-m3.onnx")
MODELO = "BAAI/bge-m3"
modelo = SentenceTransformer(MODELO)
pregunta = "¿Quién es Jesús?"
tokenizer = AutoTokenizer.from_pretrained(MODELO)

class EmbedderBGE(torch.nn.Module):
    def __init__(self, nombre):
        super().__init__()
        self.backbone = AutoModel.from_pretrained(nombre) 

    def forward(self, input_ids, attention_mask):
        salida = self.backbone(input_ids=input_ids, attention_mask=attention_mask) #Deja un vector por cada token

        cls = salida.last_hidden_state[:, 0] 

        return torch.nn.functional.normalize(cls, p=2, dim=1)


modelo = EmbedderBGE(MODELO).eval()
entradas = tokenizer(pregunta, return_tensors="pt", padding=True, truncation=True, max_length=512)

RUTA_TEMP  = os.path.join(CARPETA, "_temp.onnx")
RUTA_ONNX  = os.path.join(CARPETA, "bge-m3.onnx")
torch.onnx.export(
    modelo,
    (entradas["input_ids"], entradas["attention_mask"]),
    RUTA_TEMP,
    input_names=["input_ids", "attention_mask"],
    output_names=["embedding"],
    dynamic_axes={
        "input_ids":      {0: "batch", 1: "seq"},
        "attention_mask": {0: "batch", 1: "seq"},
        "embedding":      {0: "batch"},
    },
    opset_version=17,
    dynamo=False,
)

modelo_onnx = onnx.load(RUTA_TEMP, load_external_data=True)
onnx.save_model(
    modelo_onnx,
    RUTA_ONNX,
    save_as_external_data=True,
    all_tensors_to_one_file=True,
    location="bge-m3.onnx.data",
    size_threshold=0,
)



CONSERVAR = {"bge-m3.onnx", "bge-m3.onnx.data"}
borrados = 0
for nombre in os.listdir(CARPETA):
    if nombre not in CONSERVAR:
        ruta = os.path.join(CARPETA, nombre)
        if os.path.isfile(ruta):
            os.remove(ruta)
            borrados += 1


