package com.example.app_android.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.TextFieldDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.app_android.ui.theme.AlhambraArena
import com.example.app_android.ui.theme.AlhambraCrema
import com.example.app_android.ui.theme.AlhambraTerracota
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MessageBar(
    value: String,
    onValueChange: (String) -> Unit,
    onSend: () -> Unit,
    enabled: Boolean = true
) {
    Row (
        modifier = Modifier
            .fillMaxWidth()
            .background(AlhambraArena)
            .padding(horizontal = 10.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        TextField(
            value = value,
            onValueChange = onValueChange,
            placeholder = { Text("Escribe un mensaje...") },
            modifier = Modifier.weight(1f),
            shape = RoundedCornerShape(244.dp),
            colors = TextFieldDefaults.colors(
                focusedContainerColor = Color.White,
                unfocusedTextColor = Color.White,
                focusedIndicatorColor = Color.Transparent,
                unfocusedIndicatorColor = Color.Transparent,
                cursorColor = AlhambraTerracota
            ),
            maxLines = 4
        )

        IconButton(
            onClick  = onSend,
            enabled = enabled,
            modifier = Modifier
                .padding(start = 8.dp)
                .size(48.dp)
                .background(AlhambraTerracota, CircleShape)
        ) {
            Icon(Icons.Filled.Send, contentDescription = "Enviar", tint = AlhambraCrema)
        }
    }
}