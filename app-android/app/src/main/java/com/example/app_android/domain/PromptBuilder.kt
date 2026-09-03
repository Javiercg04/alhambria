package com.example.app_android.domain

import android.util.Log
object PromptBuilder {

    private const val MAX_CHARACTERS = 4000
    fun build(question: String, context: String): String = buildString{
        val contextoSeguro = context.take(MAX_CHARACTERS)
        if ( contextoSeguro.isNotBlank() ) append("Contexto:\n").append(contextoSeguro).append("\n\n")
        append("Pregunta: ").append(question)
        Log.d("LITERT", "Pregunta: $question")
        Log.d("LITERT", "Contexto recuperado: $contextoSeguro")
    }
}