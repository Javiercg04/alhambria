package com.example.app_android.data.embedding

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import ai.onnxruntime.extensions.OrtxPackage
import android.content.Context
import java.io.File
import android.util.Log
import java.nio.file.Paths
import kotlin.io.path.Path

class Tokenizer (private val context: Context) {

    private val env = OrtEnvironment.getEnvironment()
    private lateinit var session : OrtSession

    data class Encoding(val ids: LongArray, val masks: LongArray)

    fun init(){
        val file = assetToFile("tokenizer.onnx")
        val opts = OrtSession.SessionOptions()
        opts.registerCustomOpLibrary(OrtxPackage.getLibraryPath())
        if (!::session.isInitialized){
            session = env.createSession(file.absolutePath, opts)
        }
    }

    fun encode(text: String) : Encoding {
        val inputName = session.inputNames.iterator().next()
        val inputTensor = OnnxTensor.createTensor(env, arrayOf(text))
        val result = session.run(mapOf(inputName to inputTensor))

        val nombres = session.outputNames.toList()
        val nombreIds = nombres.firstOrNull { it.contains("input_ids") || it == "ids" } ?: nombres[0]
        val nombreMask = nombres.firstOrNull { it.contains("attention_mask") || it.contains("mask") }

        val ids = toLongArray(result.get(nombreIds).get().value)
        val mask = if (nombreMask != null)
            toLongArray(result.get(nombreMask).get().value)
        else LongArray(ids.size) { 1L }

        inputTensor.close(); result.close()

        return Encoding(ids,mask)
    }

    private fun toLongArray(v: Any?): LongArray = when (v) {
        is LongArray -> v
        is IntArray  -> LongArray(v.size) { v[it].toLong() }          // <-- tu caso: int32 -> long
        is Array<*>  -> {
            when (val fila = v[0]) {                                   // forma [1, seq]
                is LongArray -> fila
                is IntArray  -> LongArray(fila.size) { fila[it].toLong() }
                else -> error("Fila de tipo inesperado: ${fila?.javaClass}")
            }
        }
        else -> error("Salida del tokenizador con tipo inesperado: ${v?.javaClass}")
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