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
import androidx.lifecycle.lifecycleScope
import com.example.app_android.domain.InferenceAPI
import kotlinx.coroutines.launch
import org.koin.android.ext.android.inject
import android.util.Log
import org.koin.androidx.compose.koinViewModel
import com.example.app_android.data.embedding.ParityCheck
class MainActivity : ComponentActivity() {

    private val inference: InferenceAPI by inject()


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            chatAITheme {
                val vm: ChatViewModel = koinViewModel()
                ChatScreen(vm = vm)
            }

        }

    }
}
