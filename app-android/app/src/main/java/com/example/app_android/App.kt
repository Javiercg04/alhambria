package com.example.app_android

import android.app.Application
import com.example.app_android.di.AppModule
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin
import org.koin.ksp.generated.module
import android.util.Log
class App: Application() {
    override fun onCreate() {
        super.onCreate()

        Log.d("MI_APP", "========== APP ONCREATE ==========")

        startKoin {
            androidContext(this@App)
            modules(AppModule().module)
        }

        Log.d("MI_APP", "========== KOIN STARTED ==========")
    }
}