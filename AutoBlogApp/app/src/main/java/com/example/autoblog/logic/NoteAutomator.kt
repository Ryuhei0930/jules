package com.example.autoblog.logic

import android.os.Handler
import android.os.Looper
import android.webkit.WebView
import android.webkit.WebViewClient

class NoteAutomator(private val webView: WebView) {

    fun postArticle(title: String, content: String, imageUrl: String) {
        val handler = Handler(Looper.getMainLooper())

        handler.post {
            webView.webViewClient = object : WebViewClient() {
                override fun onPageFinished(view: WebView?, url: String?) {
                    super.onPageFinished(view, url)
                    // Check if we are on the new note page (URL might vary, e.g., with query params)
                    if (url?.contains("note.com/notes/new") == true) {
                        // Delay slightly to ensure editor is ready (React/Vue rendering)
                        Handler(Looper.getMainLooper()).postDelayed({
                            injectContent(title, content, imageUrl)
                        }, 3000)
                    }
                }
            }
            webView.loadUrl("https://note.com/notes/new")
        }
    }

    private fun injectContent(title: String, content: String, imageUrl: String) {
        // Simple escaping for JS string injection
        val escapedTitle = title.replace("\"", "\\\"").replace("\n", "\\n")
        // Convert newlines to <br> for HTML injection in contenteditable
        val escapedContent = content.replace("\"", "\\\"").replace("\n", "<br>")
        val finalBody = "$escapedContent<br><br><img src=\"$imageUrl\" alt=\"Generated Image\" style=\"max-width:100%;\"><br><a href=\"$imageUrl\">画像リンク</a>"

        val js = """
            (function() {
                function simulateInput(element, value) {
                    var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeInputValueSetter.call(element, value);
                    var event = new Event('input', { bubbles: true });
                    element.dispatchEvent(event);
                }

                // Title
                var titleInput = document.querySelector('input[placeholder="記事タイトル"]');
                if (!titleInput) titleInput = document.querySelector('input[aria-label="記事タイトル"]');

                if (titleInput) {
                    simulateInput(titleInput, "$escapedTitle");
                } else {
                    console.log("Title input not found");
                }

                // Body (Contenteditable)
                var editor = document.querySelector('.editor-content [contenteditable="true"]');
                if (!editor) editor = document.querySelector('[data-editor-type="note"] [contenteditable="true"]');

                if (editor) {
                    editor.focus();
                    // Using execCommand for better compatibility with contenteditable editors
                    document.execCommand('insertHTML', false, "$finalBody");
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                } else {
                    console.log("Editor not found");
                }
            })();
        """.trimIndent()

        webView.evaluateJavascript(js, null)
    }
}
