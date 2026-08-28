package com.example.app_android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.app_android.model.Message
import com.example.app_android.ui.theme.AlhambraCrema
import com.example.app_android.ui.theme.AlhambraNaranja
import com.example.app_android.ui.theme.AlhambraTextoOscuro
import com.example.app_android.ui.theme.AlhambraTerracota

@Composable
fun ChatBubble(message: Message) {
    val fromUser = message.isUser
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = if (fromUser) Alignment.End else Alignment.Start
    ) {
        Box(
            modifier = Modifier
                .widthIn(max = 300.dp)
                .background(
                    color = if (fromUser) AlhambraNaranja else AlhambraCrema,
                    shape = RoundedCornerShape(
                        topStart = 16.dp,
                        topEnd = 16.dp,
                        bottomStart = if (fromUser) 16.dp else 4.dp,
                        bottomEnd = if (fromUser) 4.dp else 16.dp
                    )
                )
                .padding(horizontal = 14.dp, vertical = 10.dp)
        ) {
            Text(
                text = message.text.toString(),
                color = if (fromUser) Color.White else AlhambraTextoOscuro,
                fontSize = 15.sp
            )
        }

        // Tiempo de respuesta bajo cada mensaje de la IA
        message.responseTimeMS?.let { ms ->
            val metricsText = buildString {
                append("Respondió en %.1f s".format(ms / 1000.0))
                message.tokenCount?.let {
                    token -> append(" - $token tok")
                }
                message.tokensPerSecond?.let {
                    tokens -> append(" - %.1f tk/s".format(tokens))
                }
            }
            Text(
                text = metricsText,
                color = AlhambraTerracota.copy(alpha = 0.75f),
                fontSize = 11.sp,
                modifier = Modifier.padding(top = 3.dp, start = 6.dp, end = 6.dp)
            )
        }
    }
}