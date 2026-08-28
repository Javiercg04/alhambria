package com.example.app_android.data.embedding

import android.content.Context
import android.util.Log
import org.json.JSONArray
import org.koin.core.annotation.Single
import kotlin.math.sqrt
@Single
class ParityCheck(
    private val context: Context,
    private val embedder: OnnxEmbedder
) {

    fun run() {
        try {
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
                val ok = sim > 0.98f
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