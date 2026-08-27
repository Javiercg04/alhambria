package com.example.app_android.viewmodel

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.app_android.model.Message
import com.example.app_android.data.index.Retriever
import com.example.app_android.domain.ChatRepository
import com.example.app_android.domain.InferenceAPI
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import org.koin.android.annotation.KoinViewModel

@KoinViewModel
class ChatViewModel(
    private val inferenceAPI: InferenceAPI,
    private val chatRepository: ChatRepository
) : ViewModel() {

    private val _listo = MutableStateFlow(false)
    val listo = _listo.asStateFlow()

    private val _progreso = MutableStateFlow(0f)
    val progreso = _progreso.asStateFlow()

    init {
        viewModelScope.launch {
            inferenceAPI.initialize { p -> _progreso.value = p}
            _listo.value = true
        }
    }
    suspend fun responder(pregunta: String): String? =
        chatRepository.ask(pregunta)

}
