package com.example.app_android.data.index

import kotlin.math.sqrt

fun coseno(a: FloatArray, b: FloatArray): Float {
    var dot = 0f; var na = 0f; var nb = 0f
    for (i in a.indices) {
        dot += a[i]*b[i]
        na += a[i]*a[i]
        nb += b[i]*b[i]
    }
    val denom = Math.sqrt((na * nb).toDouble()).toFloat()
    return if( denom == 0F ) 0F else dot/denom
}