package com.example.app_android.ui.screen

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.app_android.model.Message
import com.example.app_android.ui.components.ChatBubble
import com.example.app_android.ui.components.MessageBar
import com.example.app_android.ui.components.TopBar
import com.example.app_android.ui.theme.AlhambraArena
import com.example.app_android.ui.theme.AlhambraCrema
import com.example.app_android.ui.theme.AlhambraTerracota
import com.example.app_android.ui.theme.AlhambraTextoOscuro
import kotlinx.coroutines.launch
import com.example.app_android.viewmodel.ChatViewModel
import android.util.Log
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.material3.LinearProgressIndicator

@Composable
fun ChatScreen(vm: ChatViewModel) {
    var message by remember {
        mutableStateOf(
            listOf(
                Message(
                    text = "Hola. ¿En que puedo ayudarte hoy?",
                    isUser = false,
                    responseTimeMS = 800
                )
            )
        )
    }

    val listo by vm.listo.collectAsState()
    var input by remember { mutableStateOf("") }
    var waiting by remember { mutableStateOf(false) }

    val listState = rememberLazyListState()
    val scope = rememberCoroutineScope()

    fun scrollToBottom() = scope.launch {
        val total = message.size + if (waiting) 1 else 0
        if ( total > 0) listState.animateScrollToItem(total - 1)
    }

    fun send() {
        val text = input.trim()
        if (text.isEmpty() || waiting) return

        message = message + Message(text, isUser = true)
        input = ""
        waiting = true
        scrollToBottom()


        val start = System.currentTimeMillis()
        scope.launch {
            val respuesta = vm.responder(text)
            Log.d("LLM_RESULT", "RESULTADO COMPLETO = [$respuesta]")
            Log.d("LLM_RESULT", "RESULTADO ES NULL = ${respuesta == null}")
            val elapsedMs = System.currentTimeMillis() - start

            message = message + Message(
                text = respuesta,
                isUser = false,
                responseTimeMS = elapsedMs
            )
            waiting = false
            scrollToBottom()
        }
    }

    Scaffold(
        topBar = { TopBar() },
        containerColor = AlhambraArena
    ) {
        innerPadding ->

        if(!listo) {
            val progreso by vm.progreso.collectAsState()
            Column(
                Modifier.fillMaxSize().padding(innerPadding),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text("Preparando el Asistente", color = AlhambraTextoOscuro)
                Spacer(Modifier.height(16.dp))
                if ( progreso > 0f && progreso < 1f)
                    LinearProgressIndicator(progress = { progreso })
                else
                    CircularProgressIndicator(color = AlhambraTerracota)
            }
        } else {
            Column(
                Modifier.fillMaxSize().padding(innerPadding)
            ) {
                LazyColumn(
                    state = listState,
                    modifier = Modifier.weight(1f).fillMaxWidth(),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 12.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    items(message) { m -> ChatBubble(m) }
                    if (waiting) item { TypingIndicator() }
                }

                MessageBar(
                    value = input,
                    onValueChange = { input = it },
                    onSend = { send() },
                    enabled = !waiting && listo
                )
            }
        }
    }
}

@Composable
fun TypingIndicator() {
    Box(
        modifier = Modifier
            .background(AlhambraCrema, RoundedCornerShape(16.dp))
            .padding(horizontal = 14.dp, vertical = 10.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            CircularProgressIndicator(
                modifier = Modifier.size(14.dp),
                strokeWidth = 2.dp,
                color = AlhambraTerracota
            )
            Text("  Escribiendo…", color = AlhambraTextoOscuro, fontSize = 13.sp)
        }
    }
}