import src.extraccion as e
for pdf in ["N_22_08.pdf", "martin_alcazaba_torre_homenaje.pdf"]:
    bruto = e.extraer_texto(f"corpus/{pdf}", min_pt=0)
    filtrado = e.extraer_texto(f"corpus/{pdf}")
    limpio = e.limpiar_texto_completo(filtrado)
    print(f"{pdf}: {len(bruto.split())} -> {len(filtrado.split())} -> {len(limpio.split())}")


t = e.limpiar_texto_completo(e.extraer_texto("corpus/martin_alcazaba_torre_homenaje.pdf"))
print(len(t.split()), "palabras")
print("ABSTRACT" in t, "KEY WORDS" in t, "The following article" in t)

salidas = tok.run(None, {tok.get_inputs()[0].name: np.array(["¿Dónde está la Torre de la Vela?"])})
for i, s in enumerate(salidas):
    print(i, tok.get_outputs()[i].name, np.asarray(s).shape, np.asarray(s).reshape(-1)[:20])