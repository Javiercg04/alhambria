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
@Single(binds = [InferenceAPI::class])
class LiteRT (
    private val modelProvider: ModelProvider,
    private val appContext: Context,
) : InferenceAPI() {

    private var engine: Engine? = null
    private var conversationConfig: ConversationConfig? = null


    override suspend fun initialize(onProgress: (Float) -> Unit) = withContext(Dispatchers.IO){
        if(engine != null) return@withContext
        val path = modelProvider.ensureModel(appContext, onProgress)
        engine = Engine(EngineConfig(
                modelPath = path,
                backend = Backend.CPU(),
                cacheDir = appContext.cacheDir.path,
            )
        ).apply { initialize() }

        conversationConfig =
            ConversationConfig(
                systemInstruction = Contents.of(
                    "Eres un guía de la Alhambra así que habla de esa manera. Además responde de forma completa combinando la información del contexto"+
                            "y únicamente si la pregunta no es respecto a la Alhambra, di que no lo sabes. resta especial atención a quién originó o adoptó cada dato; no confundas quien creó algo con quien lo adoptó de una fuente anterior. No menciones la fuente ni el contexto, ni de dónde sacas la información "
                ),
                samplerConfig = SamplerConfig(
                    topK = 40,
                    topP = 0.95,
                    temperature = 0.7
                ),
            )

    }

    override suspend fun getResponse(prompt: String): String? = withContext(Dispatchers.IO){
        val eng = engine ?: return@withContext null
        val cfg = conversationConfig ?: return@withContext null
        try {
            eng.createConversation(cfg).use {
                conv ->
                Log.d("LITERT", "Contexto recuperado OK, longitud=${prompt.length}")
                val raw = conv.sendMessage(prompt).toString()
                Log.d("LITERT", "sendMessage devolvió")
                val respuesta = limpiarRazonamiento(raw)
                respuesta
            }
        } catch (e: Exception) {
            Log.e("LITERT", "ERROR EN sendMessage()", e)
            null
        }
    }

    override fun close() {
        engine?.close()
        conversationConfig = null
        engine = null
    }

    private fun limpiarRazonamiento(texto: String): String =
        if ("</think>" in texto) texto.substringAfter("</think>").trim()
        else texto.trim()

}