package com.example.autoblog.api

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class AnthropicClient(private val apiKey: String) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(60, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()
    private val gson = Gson()
    private val mediaType = "application/json; charset=utf-8".toMediaType()

    fun generateMessage(model: String, messages: List<ChatMessage>): String {
        val requestBody = AnthropicRequest(model = model, messages = messages, max_tokens = 1024)
        val json = gson.toJson(requestBody)
        val body = json.toRequestBody(mediaType)

        val request = Request.Builder()
            .url("https://api.anthropic.com/v1/messages")
            .addHeader("x-api-key", apiKey)
            .addHeader("anthropic-version", "2023-06-01")
            .addHeader("content-type", "application/json")
            .post(body)
            .build()

        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Unexpected code $response: ${response.body?.string()}")
            val responseBody = response.body?.string() ?: throw IOException("Empty response")
            val anthropicResponse = gson.fromJson(responseBody, AnthropicResponse::class.java)
            return anthropicResponse.content.firstOrNull()?.text ?: ""
        }
    }
}
