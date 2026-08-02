package com.example.app_android.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.example.app_android.ui.theme.AlhambraCrema
import com.example.app_android.ui.theme.AlhambraNaranjaClaro
import com.example.app_android.ui.theme.AlhambraTerracota
import java.sql.Time

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopBar (
    title: String = "Asistente IA",
    subtitle: String = "En línea"
) {
    TopAppBar(
        title = {
            Column {
                Text(title, color = AlhambraCrema, fontSize = 17.sp, fontWeight = FontWeight.Medium)
                Text(subtitle, color = AlhambraNaranjaClaro, fontSize = 12.sp)
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(containerColor = AlhambraTerracota)
    )
}