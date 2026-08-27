package com.example.app_android.di

import android.content.ContentResolver
import android.content.Context
import org.koin.core.annotation.ComponentScan
import org.koin.core.annotation.Factory
import org.koin.core.annotation.Module

@Module
@ComponentScan("com.example.app_android")
class AppModule{
    @Factory
    fun contentResolver(context: Context): ContentResolver = context.contentResolver
}