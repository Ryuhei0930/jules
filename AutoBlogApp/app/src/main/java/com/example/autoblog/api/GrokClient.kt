package com.example.autoblog.api

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class GrokClient(private val apiKey: String) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()
    private val mediaType = "application/json; charset=utf-8".toMediaType()

    fun generateChat(messages: List<ChatMessage>): String {
        val requestBody = ChatRequest(model = "grok-beta", messages = messages)
        val json = gson.toJson(requestBody)
        val body = json.toRequestBody(mediaType)

        val request = Request.Builder()
            .url("https://api.x.ai/v1/chat/completions")
            .addHeader("Authorization", "Bearer $apiKey")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response: ${response.body?.string()}")
            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val chatResponse = gson.fromJson(responseBody, ChatResponse::class.java)
            return chatResponse.choices.firstOrNull()?.message?.content ?: ""
        }
    }
}
