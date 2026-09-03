import os
from onnxruntime.quantization import quantize_dynamic, QuantType

CARPETA = os.path.join("..","salida","modelo")
RUTA_ONNX = os.path.join(CARPETA,"bge-m3.onnx")
RUTA_INT = os.path.join(CARPETA,"bge-m3.int8.onnx")

quantize_dynamic(
    model_input = RUTA_ONNX,
    model_output = RUTA_INT,
    weight_type = QuantType.QInt8,
    use_external_data_format=True,
)

