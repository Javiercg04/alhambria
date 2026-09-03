package com.example.app_android.data.llm

import android.content.Context
import com.example.app_android.domain.InferenceAPI
import com.google.ai.edge.litertlm.Backend
import com.google.ai.edge.litertlm.Contents
import com.google.ai.edge.litertlm.ConversationConfig
import com.google.ai.edge.litertlm.Engine
import com.google.ai.edge.litertlm.EngineConfig
import com.google.ai.edge.litertlm.SamplerConfig
import kotlinx.coroutines.Dispatchers
import org.koin.core.annotation.Single
import kotlinx.coroutines.withContext
import android.util.Log

data class LLMResponse(
    val text: String?,
    val generationTimeMs: Long,
    val generationTokens: Int,
    val tokensPerSecond: Double
)
@Single(binds = [InferenceAPI::class])
class LiteRT (
    private val modelProvider: ModelProvider,
    private val appContext: Context,
) : InferenceAPI() {

    private var engine: Engine? = null
    private var conversationConfig: ConversationConfig? = null


    override suspend fun initialize(chosenLlm: AvailableLlm,onProgress: (Float) -> Unit) = withContext(Dispatchers.IO){
        if(engine != null) return@withContext


        val llmPath = modelProvider.ensureLlmModel(appContext, chosenLlm, onProgress)

        engine = Engine(EngineConfig(
                modelPath = llmPath,
                backend = Backend.CPU(),
                cacheDir = appContext.cacheDir.path,
            )
        ).apply { initialize() }

        conversationConfig =
            ConversationConfig(
                /*
                systemInstruction = Contents.of(
                    "Eres un guía de la Alhambra así que habla de esa manera. Además responde de forma completa combinando la información del contexto"+
                            "y únicamente si la pregunta no es respecto a la Alhambra, di que no lo sabes. resta especial atención a quién originó o adoptó cada dato; no confundas quien creó algo con quien lo adoptó de una fuente anterior. No menciones la fuente ni el contexto, ni de dónde sacas la información "
                ),
                 */
                systemInstruction = Contents.of("Responde en español usando solo la información del contexto"),
                samplerConfig = SamplerConfig(
                    topK = 40,
                    topP = 0.95,
                    temperature = 0.2
                ),
            )

    }

    override suspend fun getResponse(prompt: String): String? = getResponseWithMetrics(prompt).text

    override suspend fun getResponseWithMetrics(prompt: String): LLMResponse = withContext(Dispatchers.IO){
        val activeEng = engine ?: return@withContext LLMResponse(null,0,0,0.0)
        val activeCfg = conversationConfig ?: return@withContext LLMResponse(null,0,0,0.0)
        try {
            activeEng.createConversation(activeCfg).use {
                conv ->
                Log.d("LITERT", "Contexto recuperado OK, longitud=${prompt.length}")
                val starTime = System.currentTimeMillis()
                val raw = conv.sendMessage(prompt).toString()
                val generationTimeMs = System.currentTimeMillis() - starTime
                Log.d("LITERT", "sendMessage devolvió")
                val response = cleanText(raw)

                val wordCount = response.trim()
                    .split(Regex("\\s+"))
                    .count { it.isNotBlank() }
                val tokenCount = (wordCount * 1.3).toInt()
                val tokenPerSecond = if ( generationTimeMs > 0) {
                    tokenCount / ( generationTimeMs / 1000.0 )
                } else 0.0

                LLMResponse (
                    text = response,
                    generationTimeMs = generationTimeMs,
                    generationTokens = tokenCount,
                    tokensPerSecond = tokenPerSecond,
                )
            }
        } catch (e: Exception) {
            Log.e("LITERT", "ERROR EN sendMessage()", e)
            LLMResponse(null,0,0,0.0)
        }
    }

    override fun close() {
        engine?.close()
        conversationConfig = null
        engine = null
    }

    private fun cleanText(texto: String): String =
        if ("</think>" in texto) texto.substringAfter("</think>").trim()
        else texto.trim()

}