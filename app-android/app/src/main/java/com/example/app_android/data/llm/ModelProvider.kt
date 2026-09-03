package com.example.app_android.data.llm

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.koin.core.annotation.Single
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit
import kotlin.coroutines.coroutineContext

data class ModelInfo(
    val fileName: String,
    val url: String,
)

enum class AvailableLlm(val info: ModelInfo){
    GEMMA3(
        ModelInfo(
            fileName = "gemma3-1b-int4.litertlm",
            url = "https://github.com/Javiercg04/alhambria/releases/download/v1-models/gemma3-1b-it-int4.litertlm"
        )
    ),
    QWEN3(
        ModelInfo(
            fileName = "qwen3.litertlm",
            url = "https://huggingface.co/litert-community/Qwen3-0.6B/resolve/main/qwen3_0_6b_mixed_int4.litertlm"
        )
    )
}
@Single
class ModelProvider {

    private companion object {
        const val BUFFER_SIZE = 8 * 1024

        val EMBEDDING_MODEL = ModelInfo(
            fileName = "bge-m3.int8.onnx",
            url = "https://github.com/Javiercg04/alhambria/releases/download/v1-models/bge-m3.int8.onnx"
        )
    }

    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.MILLISECONDS)
        .build()

    private fun modelFile(context: Context, fileName: String) = File(context.filesDir, fileName)

    fun isEmbeddingReady(context: Context): Boolean = modelFile(context, EMBEDDING_MODEL.fileName).exists()

    fun isLlmReady(context: Context, llm: AvailableLlm): Boolean = modelFile(context, llm.info.fileName).exists()

    suspend fun ensureLlmModel(
        context: Context,
        chosenLlm: AvailableLlm,
        onProgress: (Float) -> Unit = {},
    ): String = withContext(Dispatchers.IO) {
        val target = modelFile(context,chosenLlm.info.fileName)
        if (target.exists()) return@withContext target.absolutePath
        downloadTo(chosenLlm.info, target, onProgress)
        target.absolutePath
    }

    suspend fun ensureEmbeddingModel(
        context: Context,
        onProgress: (Float) -> Unit = {},
    ): String = withContext(Dispatchers.IO){
        val target = modelFile(context, EMBEDDING_MODEL.fileName)
        if(target.exists()) return@withContext target.absolutePath
        downloadTo(EMBEDDING_MODEL,target,onProgress)
        target.absolutePath
    }

    private suspend fun downloadTo(model: ModelInfo, target: File, onProgress: (Float) -> Unit) {
        val tmp = File(target.parentFile, "${target.name}.tmp").apply { delete() }
        try {
            val request = Request.Builder().url(model.url).build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) error("Descarga fallida: HTTP ${response.code}")
                val body = response.body ?: error("Respuesta sin cuerpo")
                val total = body.contentLength()   // -1 si el servidor no lo informa

                body.byteStream().use { input ->
                    FileOutputStream(tmp).use { output ->
                        val buffer = ByteArray(BUFFER_SIZE)
                        var downloaded = 0L
                        var lastPct = -1
                        var read: Int
                        while (input.read(buffer).also { read = it } != -1) {
                            coroutineContext.ensureActive()
                            output.write(buffer, 0, read)
                            downloaded += read
                            if (total > 0) {
                                val pct = (downloaded * 100 / total).toInt()
                                if (pct != lastPct) {
                                    lastPct = pct
                                    onProgress(pct / 100f)
                                }
                            }
                        }
                        output.flush()
                    }
                }
            }
            if (!tmp.renameTo(target)) error("No se pudo finalizar el archivo del modelo")
        } catch (e: Exception) {    
            tmp.delete()
            throw e
        }
    }
}