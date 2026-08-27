package com.example.app_android.data.embedding

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import java.nio.LongBuffer
import java.io.File
import android.content.Context
import android.util.Log
import com.example.app_android.data.embedding.Tokenizer
import org.koin.core.annotation.Single

@Single
class OnnxEmbedder(private val context: Context) {

    private val env = OrtEnvironment.getEnvironment()
    private val session: OrtSession = run {
        val onnxfile = assetToFile("bge-m3.int8.onnx")
        env.createSession(onnxfile.absolutePath, OrtSession.SessionOptions())
            .also { Log.d("RAG", "inputs=${it.inputNames} outputs=${it.outputNames}") }
    }

    fun embed(texto: String): FloatArray{
        val tokenizer = Tokenizer(context)
        tokenizer.init()
        val enc = tokenizer.encode(texto)
        val id = enc.ids
        val mask = enc.masks
        val shape = longArrayOf(1, id.size.toLong())

        val idsTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(id), shape)
        val maskTensor = OnnxTensor.createTensor(env, LongBuffer.wrap(mask), shape)

        val result = session.run(mapOf("input_ids" to idsTensor, "attention_mask" to maskTensor))
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

    private fun assetToFile(assetName: String): File {
        val storageFile = File(context.filesDir,assetName)
        val waitTam = context.assets.openFd(assetName).length
        if(!storageFile.exists() || storageFile.length() != waitTam){
            context.assets.open(assetName).use {
                input -> storageFile.outputStream().use {
                    output -> input.copyTo(output)
            }
            }
        }
        return storageFile
    }

}