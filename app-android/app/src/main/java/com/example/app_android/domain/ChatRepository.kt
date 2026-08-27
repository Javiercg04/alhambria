package com.example.app_android.domain

import com.example.app_android.data.index.Retriever
import org.koin.core.annotation.Single

@Single
class ChatRepository(
    private val inferenceAPI: InferenceAPI,
    private val retriever: Retriever,
) {
    suspend fun ask(question: String): String?{
        val resultados = retriever.buscar(question)
        val contexto = resultados.joinToString("\n\n") { it.first }
        val prompt = PromptBuilder.build(question,contexto)
        val resultado = inferenceAPI.getResponse(prompt)
        return resultado
    }
}