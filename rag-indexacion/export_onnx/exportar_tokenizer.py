from onnxruntime_extensions import gen_processing_models
from transformers import AutoTokenizer
import onnx

tok = AutoTokenizer.from_pretrained("BAAI/bge-m3")
pre, _ = gen_processing_models(tok, pre_kwargs={})   # pre = tokenizador
onnx.save(pre, "tokenizer.onnx")
print("tokenizer.onnx generado")