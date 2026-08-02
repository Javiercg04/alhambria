package com.example.app_android.data.database

import java.io.File
import android.content.Context
import java.nio.ByteBuffer
import java.nio.ByteOrder

class LeerDB (private val context: Context) {

    private var nombreDB: String = "rag.db"
    data class Indice(
        val textos: List<String>,
        val vectores: List<FloatArray>
    )

    fun cargarBaseDatos(): Indice {
        val textos = ArrayList<String>()
        val vectores = ArrayList<FloatArray>()
        val dbFile = assetToFile(nombreDB)
        val db = android.database.sqlite.SQLiteDatabase.openDatabase(
            dbFile.absolutePath,
            null,
            android.database.sqlite.SQLiteDatabase.OPEN_READONLY
        )

        val cursor = db.rawQuery("SELECT texto, embedding, fuente FROM chunks ORDER BY id", null)
        cursor.use {
            while ( it.moveToNext() ) {
                textos.add(it.getString(0))
                val blob = it.getBlob(1)
                vectores.add(bytesToFloatArray(blob))
            }
        }

        db.close()
        return Indice(textos,vectores)
    }


    private fun bytesToFloatArray(byte: ByteArray): FloatArray {
        val blobBytes = ByteBuffer.wrap(byte).order(ByteOrder.LITTLE_ENDIAN)
        return FloatArray(byte.size / 4) { blobBytes.float }
    }

    private fun assetToFile(assetName: String): File {
        val storageFile = File(context.filesDir,assetName)
        if(!storageFile.exists()){
            context.assets.open(assetName).use {
                    input -> storageFile.outputStream().use {
                    output -> input.copyTo(output)
            }
            }
        }
        return storageFile
    }
}