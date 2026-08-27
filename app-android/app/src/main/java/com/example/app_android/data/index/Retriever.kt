package com.example.app_android.data.index

import android.content.Context
import com.example.app_android.data.database.LeerDB
import com.example.app_android.data.embedding.OnnxEmbedder
import com.example.app_android.data.index.coseno
import org.koin.core.annotation.Single

@Single
class Retriever (
    private val context: Context,
    private val embedder: OnnxEmbedder,
    private val loader: LeerDB
) {
    private var textos: List<String> = emptyList()
    private var vectores: List<FloatArray> = emptyList()

    init {
        cargarIndice()
    }

    fun cargarIndice() {
        val indice = loader.cargarBaseDatos()
        textos = indice.textos
        vectores = indice.vectores
    }

    fun buscar( pregunta: String, topK: Int = 4): List<Pair<String, Float>> {
        val vec = embedder.embed(pregunta)
        val candidatos = vectores.mapIndexed { i,v -> i to v }
        val mejores = obtenerTopKSimilares(vec, candidatos, topK)
        return mejores.map { r -> textos[r.id] to r.similitud }
    }
}