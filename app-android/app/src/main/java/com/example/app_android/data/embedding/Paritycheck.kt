package com.example.app_android.data.embedding

import android.content.Context
import android.util.Log
import org.json.JSONArray
import kotlin.math.sqrt

/**
 * Verificación de paridad del embedder, pensada para lanzarse DESDE LA APP
 * (no como androidTest). Lee golden.json de los assets de la app, embebe cada
 * pregunta con OnnxEmbedder y compara por coseno contra el vector de Python.
 *
 * Uso desde MainActivity, en un hilo:
 *     ParityCheck(applicationContext).run()
 */
class ParityCheck(private val context: Context) {

    fun run() {
        try {
            // 1) Cargar tokenizador + embedder (lo mismo que en producción)
            val tokenizer = Tokenizer(context)
            val embedder = OnnxEmbedder(context)
            tokenizer.init()


            // 2) Leer el golden.json de los assets de la APP
            val json = context.assets.open("golden.json").bufferedReader().use { it.readText() }
            val arr = JSONArray(json)

            var todasOk = true
            for (i in 0 until arr.length()) {
                val o = arr.getJSONObject(i)
                val pregunta = o.getString("pregunta")
                val v = o.getJSONArray("vector")
                val esperado = FloatArray(v.length()) { v.getDouble(it).toFloat() }

                val obtenido = embedder.embed(pregunta)
                val sim = coseno(obtenido, esperado)
                val ok = sim > 0.999f
                if (!ok) todasOk = false

                Log.d("RAG", "paridad «$pregunta»  sim=${"%.5f".format(sim)}  ${if (ok) "OK" else "FALLO"}")
            }

            Log.d("RAG", if (todasOk) "PARIDAD SELLADA: embedder correcto ✓"
            else "PARIDAD ROTA: revisar (sim baja = fallo real, no redondeo)")
        } catch (e: Throwable) {
            Log.e("RAG", "ParityCheck FALLO: ${e.message}")
        }
    }

    private fun coseno(a: FloatArray, b: FloatArray): Float {
        var dot = 0f; var na = 0f; var nb = 0f
        for (i in a.indices) { dot += a[i]*b[i]; na += a[i]*a[i]; nb += b[i]*b[i] }
        return dot / (sqrt(na) * sqrt(nb))
    }
}