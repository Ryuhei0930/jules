package com.example.autoblog

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.autoblog.api.AnthropicClient
import com.example.autoblog.api.GeminiClient
import com.example.autoblog.api.OpenAiClient
import com.example.autoblog.logic.ContentGenerator
import com.example.autoblog.logic.NoteAutomator
import com.example.autoblog.logic.RssFetcher
import com.example.autoblog.utils.PreferencesManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Calendar
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var prefs: PreferencesManager
    private lateinit var tvLog: TextView
    private lateinit var webView: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = PreferencesManager(this)
        tvLog = findViewById(R.id.tvLog)
        webView = findViewById(R.id.webView)

        setupWebView()
        setupUI()

        checkNotificationPermission()
        checkNotificationIntent()
    }

    private fun checkNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33) { // Android 13 (TIRAMISU)
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.POST_NOTIFICATIONS), 101)
            }
        }
    }

    private fun setupWebView() {
        webView.settings.javaScriptEnabled = true
        webView.settings.domStorageEnabled = true
        webView.webViewClient = WebViewClient()
        // Load note login page initially or on button click
        webView.loadUrl("https://note.com/login")
    }

    private fun setupUI() {
        val etOpenAi = findViewById<EditText>(R.id.etOpenAiKey)
        val etAnthropic = findViewById<EditText>(R.id.etAnthropicKey)
        val etGemini = findViewById<EditText>(R.id.etGeminiKey)
        val etGrok = findViewById<EditText>(R.id.etGrokKey)
        val etRss = findViewById<EditText>(R.id.etRssUrl)

        etOpenAi.setText(prefs.openAiKey)
        etAnthropic.setText(prefs.anthropicKey)
        etGemini.setText(prefs.geminiKey)
        etGrok.setText(prefs.grokKey)
        etRss.setText(prefs.rssUrl)

        findViewById<Button>(R.id.btnSave).setOnClickListener {
            prefs.openAiKey = etOpenAi.text.toString()
            prefs.anthropicKey = etAnthropic.text.toString()
            prefs.geminiKey = etGemini.text.toString()
            prefs.grokKey = etGrok.text.toString()
            prefs.rssUrl = etRss.text.toString()
            Toast.makeText(this, "Settings Saved", Toast.LENGTH_SHORT).show()
        }

        findViewById<Button>(R.id.btnRunManual).setOnClickListener {
            runManualGeneration()
        }

        findViewById<Button>(R.id.btnSchedule).setOnClickListener {
            scheduleDailyWork()
        }

        findViewById<Button>(R.id.btnToggleWebView).setOnClickListener {
            if (webView.visibility == View.VISIBLE) {
                webView.visibility = View.GONE
            } else {
                webView.visibility = View.VISIBLE
            }
        }
    }

    private fun scheduleDailyWork() {
        val workRequest = PeriodicWorkRequestBuilder<DailyWorker>(24, TimeUnit.HOURS)
            .setInitialDelay(calculateInitialDelay(), TimeUnit.MILLISECONDS)
            .build()

        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "DailyBlogWork",
            ExistingPeriodicWorkPolicy.UPDATE,
            workRequest
        )
        Toast.makeText(this, "Scheduled for 8:00 AM daily", Toast.LENGTH_SHORT).show()
    }

    private fun calculateInitialDelay(): Long {
        val calendar = Calendar.getInstance()
        val now = System.currentTimeMillis()

        calendar.set(Calendar.HOUR_OF_DAY, 8)
        calendar.set(Calendar.MINUTE, 0)
        calendar.set(Calendar.SECOND, 0)

        if (calendar.timeInMillis <= now) {
            calendar.add(Calendar.DAY_OF_YEAR, 1)
        }
        return calendar.timeInMillis - now
    }

    private fun checkNotificationIntent() {
        if (intent.getBooleanExtra("EXTRA_FROM_NOTIFICATION", false)) {
            val draftPrefs = getSharedPreferences("autoblog_draft", Context.MODE_PRIVATE)
            val title = draftPrefs.getString("draft_title", "") ?: ""
            val content = draftPrefs.getString("draft_content", "") ?: ""
            val imageUrl = draftPrefs.getString("draft_image_url", "") ?: ""

            if (title.isNotEmpty() && content.isNotEmpty()) {
                log("Loading draft from notification...")
                Toast.makeText(this, "Loading Draft...", Toast.LENGTH_SHORT).show()
                // Show WebView and run automation
                webView.visibility = View.VISIBLE
                val automator = NoteAutomator(webView)
                automator.postArticle(title, content, imageUrl)

                // Clear draft info from prefs to avoid re-triggering?
                // Better keep it until successfully posted, but we can't detect success easily.
                // Let's just log.
                log("Automation started for: $title")
            }
        }
    }

    private fun runManualGeneration() {
        log("Starting manual generation...")
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val rssFetcher = RssFetcher()
                val items = rssFetcher.fetchRss(prefs.rssUrl)
                log("Fetched ${items.size} RSS items")

                if (items.isEmpty()) {
                    log("No news found.")
                    return@launch
                }

                val generator = ContentGenerator(
                    GeminiClient(prefs.geminiKey),
                    AnthropicClient(prefs.anthropicKey),
                    OpenAiClient(prefs.openAiKey)
                )

                log("Generating content...")
                val (content, imageUrl) = generator.generateBlogContent(items)

                log("Content Generated. Image URL: $imageUrl")

                withContext(Dispatchers.Main) {
                    Toast.makeText(this@MainActivity, "Generation Complete! Showing preview...", Toast.LENGTH_LONG).show()
                    webView.visibility = View.VISIBLE
                    val automator = NoteAutomator(webView)
                    automator.postArticle(items.first().title, content, imageUrl)
                }

            } catch (e: Exception) {
                log("Error: ${e.message}")
                e.printStackTrace()
            }
        }
    }

    private fun log(message: String) {
        lifecycleScope.launch(Dispatchers.Main) {
            tvLog.append("\n$message")
        }
    }
}
