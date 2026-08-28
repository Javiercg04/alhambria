package com.example.app_android.model

data class Message (
    val text: String?,
    val isUser: Boolean,
    val responseTimeMS: Long? = null,
    val tokenCount: Int? = null,
    val tokensPerSecond: Double? = null
)