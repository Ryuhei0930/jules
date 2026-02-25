package com.example.autoblog

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.example.autoblog.api.AnthropicClient
import com.example.autoblog.api.GeminiClient
import com.example.autoblog.api.OpenAiClient
import com.example.autoblog.logic.ContentGenerator
import com.example.autoblog.logic.RssFetcher
import com.example.autoblog.utils.PreferencesManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class DailyWorker(appContext: Context, workerParams: WorkerParameters) :
    CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        val prefs = PreferencesManager(applicationContext)

        // 1. Fetch RSS
        val rssFetcher = RssFetcher()
        val items = try {
            rssFetcher.fetchRss(prefs.rssUrl)
        } catch (e: Exception) {
            e.printStackTrace()
            return@withContext Result.retry()
        }

        if (items.isEmpty()) return@withContext Result.success()

        // 2. Generate Content
        val generator = ContentGenerator(
            GeminiClient(prefs.geminiKey),
            AnthropicClient(prefs.anthropicKey),
            OpenAiClient(prefs.openAiKey)
        )

        try {
            val (content, imageUrl) = generator.generateBlogContent(items)
            val title = items.first().title

            // 3. Save Content to Prefs
            val editor = applicationContext.getSharedPreferences("autoblog_draft", Context.MODE_PRIVATE).edit()
            editor.putString("draft_title", title)
            editor.putString("draft_content", content)
            editor.putString("draft_image_url", imageUrl)
            editor.apply()

            // 4. Show Notification
            showNotification(title)

            Result.success()
        } catch (e: Exception) {
            e.printStackTrace()
            Result.failure()
        }
    }

    private fun showNotification(title: String) {
        val notificationManager =
            applicationContext.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "daily_blog_channel"

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                channelId,
                "Daily Blog Generation",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            notificationManager.createNotificationChannel(channel)
        }

        val intent = Intent(applicationContext, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
            putExtra("EXTRA_FROM_NOTIFICATION", true)
        }

        val pendingIntent = PendingIntent.getActivity(
            applicationContext,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(applicationContext, channelId)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("ブログ記事が生成されました")
            .setContentText("「$title」の下書きを確認して投稿してください。")
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setContentIntent(pendingIntent)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(1001, notification)
    }
}
