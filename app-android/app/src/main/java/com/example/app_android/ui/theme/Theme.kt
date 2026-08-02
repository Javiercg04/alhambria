package com.example.app_android.ui.theme

import android.app.Activity
import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val AlhambraColorScheme = lightColorScheme(
    primary = AlhambraTerracota,
    onPrimary = AlhambraCrema,
    secondary = AlhambraNaranja,
    onSecondary = Color.White,
    background = AlhambraArena,
    onBackground = AlhambraTextoOscuro,
    surface = AlhambraCrema,
    onSurface = AlhambraTextoOscuro
)


@Composable
fun chatAITheme(
    typography: Typography = Typography(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = AlhambraColorScheme,
        typography = typography,
        content = content
    )
}