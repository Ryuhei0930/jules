package com.example.autoblog.api

data class ChatMessage(val role: String, val content: String)

data class ChatRequest(
    val model: String,
    val messages: List<ChatMessage>,
    val max_tokens: Int? = null,
    val temperature: Double? = null
)

data class ChatResponse(val choices: List<Choice>) {
    data class Choice(val message: ChatMessage)
}

data class ImageRequest(
    val model: String = "dall-e-3",
    val prompt: String,
    val n: Int = 1,
    val size: String = "1024x1024"
)

data class ImageResponse(val data: List<ImageData>) {
    data class ImageData(val url: String?, val b64_json: String?)
}

// Gemini specific
data class GeminiRequest(val contents: List<GeminiContent>)
data class GeminiContent(val parts: List<GeminiPart>, val role: String = "user")
data class GeminiPart(val text: String)
data class GeminiResponse(val candidates: List<GeminiCandidate>?)
data class GeminiCandidate(val content: GeminiContent?, val finishReason: String?)

// Anthropic specific
data class AnthropicRequest(
    val model: String,
    val messages: List<ChatMessage>,
    val max_tokens: Int
)
data class AnthropicResponse(val content: List<AnthropicContent>)
data class AnthropicContent(val text: String)
