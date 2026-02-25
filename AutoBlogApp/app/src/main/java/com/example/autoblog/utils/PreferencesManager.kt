package com.example.autoblog.utils

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences = context.getSharedPreferences("autoblog_prefs", Context.MODE_PRIVATE)

    var openAiKey: String
        get() = prefs.getString("openai_key", "") ?: ""
        set(value) = prefs.edit().putString("openai_key", value).apply()

    var anthropicKey: String
        get() = prefs.getString("anthropic_key", "") ?: ""
        set(value) = prefs.edit().putString("anthropic_key", value).apply()

    var geminiKey: String
        get() = prefs.getString("gemini_key", "") ?: ""
        set(value) = prefs.edit().putString("gemini_key", value).apply()

    var grokKey: String
        get() = prefs.getString("grok_key", "") ?: ""
        set(value) = prefs.edit().putString("grok_key", value).apply()

    var rssUrl: String
        get() = prefs.getString("rss_url", "https://feeds.feedburner.com/TechCrunch/") ?: "https://feeds.feedburner.com/TechCrunch/"
        set(value) = prefs.edit().putString("rss_url", value).apply()
}
