package com.example.app_android.domain

abstract class InferenceAPI{
    abstract suspend fun initialize(onProgress: (Float) -> Unit = {})
    abstract suspend fun getResponse(prompt: String): String?
    open fun close() {}
}