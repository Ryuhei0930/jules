package com.example.autoblog.logic

import android.util.Xml
import okhttp3.OkHttpClient
import okhttp3.Request
import org.xmlpull.v1.XmlPullParser
import java.io.IOException
import java.io.StringReader

data class RssItem(
    val title: String,
    val description: String,
    val link: String,
    val pubDate: String
)

class RssFetcher {
    private val client = OkHttpClient()

    fun fetchRss(url: String): List<RssItem> {
        val request = Request.Builder().url(url).build()
        client.newCall(request).execute().use { response ->
            if (!response.isSuccessful) throw IOException("Failed to fetch RSS: $response")
            val xmlString = response.body?.string() ?: throw IOException("Empty response")
            return parseRss(xmlString)
        }
    }

    private fun parseRss(xml: String): List<RssItem> {
        val items = mutableListOf<RssItem>()
        val parser = Xml.newPullParser()
        parser.setInput(StringReader(xml))

        var eventType = parser.eventType
        var currentTag = ""
        var title = ""
        var description = ""
        var link = ""
        var pubDate = ""
        var isInsideItem = false

        while (eventType != XmlPullParser.END_DOCUMENT) {
            when (eventType) {
                XmlPullParser.START_TAG -> {
                    currentTag = parser.name
                    if (currentTag == "item") {
                        isInsideItem = true
                        title = ""
                        description = ""
                        link = ""
                        pubDate = ""
                    }
                }
                XmlPullParser.TEXT -> {
                    if (isInsideItem) {
                        val text = parser.text
                        when (currentTag) {
                            "title" -> title = text
                            "description" -> description = text
                            "link" -> link = text
                            "pubDate" -> pubDate = text
                        }
                    }
                }
                XmlPullParser.END_TAG -> {
                    if (parser.name == "item") {
                        isInsideItem = false
                        if (title.isNotEmpty()) {
                            items.add(RssItem(title, description, link, pubDate))
                        }
                    }
                    currentTag = ""
                }
            }
            eventType = parser.next()
        }
        return items
    }
}
