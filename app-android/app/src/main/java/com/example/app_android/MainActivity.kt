package com.example.app_android

import com.example.app_android.data.embedding.OnnxEmbedder
import com.example.app_android.data.database.LeerDB
import com.example.app_android.data.index.Retriever
import com.example.app_android.viewmodel.ChatViewModel

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.app_android.ui.screen.ChatScreen
import com.example.app_android.ui.theme.chatAITheme
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import com.example.app_android.data.embedding.ParityCheck

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            chatAITheme {
                val contexto = LocalContext.current
                val vm = remember {
                    val embedder = OnnxEmbedder(contexto)
                    val loader = LeerDB(contexto)
                    val retriever = Retriever(contexto, embedder, loader)
                    ChatViewModel(retriever)
                }
                ChatScreen(vm)
            }
        }

    }
}
