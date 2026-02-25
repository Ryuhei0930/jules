package com.example.autoblog.api

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class GeminiClient(private val apiKey: String) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()
    private val mediaType = "application/json; charset=utf-8".toMediaType()

    fun generateContent(prompt: String): String {
        // Gemini API expects a specific structure. The Models.kt definition should match.
        // For simplicity, we wrap prompt in user role.
        val requestBody = GeminiRequest(
            contents = listOf(GeminiContent(parts = listOf(GeminiPart(text = prompt)), role = "user"))
        )
        val json = gson.toJson(requestBody)
        val body = json.toRequestBody(mediaType)

        val request = Request.Builder()
            .url("https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key=$apiKey")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response: ${response.body?.string()}")
            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val geminiResponse = gson.fromJson(responseBody, GeminiResponse::class.java)
            return geminiResponse.candidates?.firstOrNull()?.content?.parts?.firstOrNull()?.text ?: ""
        }
    }
}
