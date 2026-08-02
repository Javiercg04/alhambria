package com.example.app_android.data.index


import java.util.PriorityQueue

data class ResultadoTopK(
    val id: Int,
    val similitud: Float
)

fun obtenerTopKSimilares(
    vectorObjetivo: FloatArray,
    candidatos: List<Pair<Int, FloatArray>>,
    k: Int
): List<ResultadoTopK> {
    if( k <= 0) return emptyList()

    val minHeap = PriorityQueue<ResultadoTopK>(compareBy { it.similitud })

    for (candidato in candidatos) {
        val(id, vector) = candidato

        if(vector.size != vectorObjetivo.size) continue
        val similitud = coseno(vectorObjetivo, vector)
        if (minHeap.size < k){
            minHeap.add(ResultadoTopK(id,similitud))
        }else{
            if ( similitud > minHeap.peek().similitud){
                minHeap.poll()
                minHeap.add(ResultadoTopK(id, similitud))
            }
        }
    }
    return minHeap.sortedByDescending { it.similitud }
}