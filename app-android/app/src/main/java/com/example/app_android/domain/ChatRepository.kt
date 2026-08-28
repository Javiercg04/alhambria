package com.example.app_android.domain

import com.example.app_android.data.index.Retriever
import com.example.app_android.data.llm.LLMResponse
import org.koin.core.annotation.Single

@Single
class ChatRepository(
    private val inferenceAPI: InferenceAPI,
    private val retriever: Retriever,
) {
    suspend fun askWithMetrics(question: String): LLMResponse {
        val results = retriever.buscar(question)
        val context = results.joinToString("\n\n") { it.first }
        val prompt = PromptBuilder.build(question,context)
        val result = inferenceAPI.getResponseWithMetrics(prompt)
        return result
    }
}