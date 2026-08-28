package com.example.app_android.data.embedding

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.nio.LongBuffer
import java.io.File
import android.content.Context
import android.util.Log
import androidx.compose.ui.platform.LocalDensity
import com.example.app_android.data.embedding.Tokenizer
import com.example.app_android.data.llm.ModelProvider
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.koin.core.annotation.Single

@Single
class OnnxEmbedder(
    private val context: Context,
    private val modelProvider: ModelProvider,
) {

    private val env = OrtEnvironment.getEnvironment()
    private var session: OrtSession? = null
    private var tokenizer: Tokenizer? = null

    suspend fun initialize(onProgress: (Float) -> Unit = {}) = withContext(Dispatchers.IO) {
        if (session != null) return@withContext
        val onnxPath = modelProvider.ensureEmbeddingModel(context, onProgress)
        tokenizer = Tokenizer(context).apply { init() }
        session = env.createSession(onnxPath, OrtSession.SessionOptions())
            .also { Log.d("RAG", "inputs=${it.inputNames} outputs=${it.outputNames}") }
    }


    fun embed(texto: String): FloatArray{
        val activeSession = session ?: error("OnnxEmbedder not Initialized")
        val tokenizer = tokenizer ?: error("Tokenizer not Initialized")
        val enc = tokenizer.encode(texto)
        val id = enc.ids
        val mask = enc.masks
        val shape = longArrayOf(1, id.size.toLong())

        val idsTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(id), shape)
        val maskTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(mask), shape)

        val result = activeSession.run(mapOf("input_ids" to idsTensor, "attention_mask" to maskTensor))
        val output = result.get("embedding").get() as OnnxTensor
        val hidden = output.info.shape.last().toInt()
        val vec = FloatArray(hidden)
        output.floatBuffer.get(vec, 0, hidden)

        idsTensor.close()
        maskTensor.close()
        result.close()
        Log.d("RAG", "output shape = ${output.info.shape.joinToString()}")
        return vec
    }

}