package com.example.app_android.domain

import com.example.app_android.data.llm.AvailableLlm
import com.example.app_android.data.llm.LLMResponse

abstract class InferenceAPI{
    abstract suspend fun initialize(chosenLlm: AvailableLlm, onProgress: (Float) -> Unit)
    abstract suspend fun getResponse(prompt: String): String?
    abstract suspend fun getResponseWithMetrics(prompt: String): LLMResponse
    open fun close() {}
}