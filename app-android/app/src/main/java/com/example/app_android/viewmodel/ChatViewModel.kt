package com.example.app_android.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.app_android.model.Message
import com.example.app_android.data.index.Retriever
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class ChatViewModel(
    private val retriever: Retriever
) : ViewModel() {

    suspend fun responder(pregunta: String): List<Pair<String, Float>> =
        withContext(Dispatchers.Default) {
            retriever.buscar(pregunta)
        }
}
