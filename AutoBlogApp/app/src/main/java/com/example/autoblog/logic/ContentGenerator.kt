package com.example.autoblog.logic

import com.example.autoblog.api.*

class ContentGenerator(
    private val geminiClient: GeminiClient,
    private val anthropicClient: AnthropicClient,
    private val openAiClient: OpenAiClient
) {

    fun generateBlogContent(newsItems: List<RssItem>): Pair<String, String> {
        // 1. ニュースの選択（最新1つ）
        val targetNews = newsItems.firstOrNull() ?: return "ニュースが見つかりませんでした。" to ""

        // 2. Geminiによる要約と解説
        val summaryPrompt = """
            以下のニュース記事を読み、一般の人にもわかるように要約し、さらに高度な技術的補足情報も付け加えてください。

            タイトル: ${targetNews.title}
            概要: ${targetNews.description}
            URL: ${targetNews.link}
        """.trimIndent()

        val summary = geminiClient.generateContent(summaryPrompt)

        // 3. Claudeによる対話台本の作成
        val dialoguePrompt = """
            あなたはAIニュース解説ブログの編集長です。
            以下のニュース要約を元に、3人のAIキャラクター（Gemini、Claude、ChatGPT）が討論する形式の記事を作成してください。

            キャラクター設定:
            - Gemini: 最新情報に詳しく、検索能力が高い。論理的で少し堅い。
            - Claude: 全体の構成を考え、バランスを取る司会進行役。知的で穏やか。
            - ChatGPT: 創造的でユニークな視点を持つ。ユーモアや画像生成のアイデアを出す。

            ニュース要約:
            $summary

            構成:
            1. 導入（Claudeから開始）
            2. ニュースの深掘り（Gemini中心）
            3. 独自の視点や未来予測（ChatGPT中心）
            4. まとめ（Claude）

            重要な指示:
            この記事はnoteで収益（投げ銭）を得ることを目的としています。
            読者が「ためになった」「面白かった」と感じてサポートしたくなるような、付加価値の高い洞察や、ウィットに富んだ会話を含めてください。
            また、記事の最後にはClaudeが丁寧に、しかしユーモアを交えてサポートをお願いする一言を添えてください。

            出力形式:
            各発言を "【キャラクター名】: 発言内容" の形式で書いてください。
        """.trimIndent()

        // 4. Claudeモデル：ユーザー指定に合わせて更新。
        // 指定: claude-haiku-4-5-20251001
        val dialogue = anthropicClient.generateMessage("claude-haiku-4-5-20251001", listOf(ChatMessage("user", dialoguePrompt)))

        // 5. ChatGPTによる画像プロンプト生成
        // 指定: gpt-5-mini-2025-08-07
        val imagePromptGenPrompt = """
            以下のAI討論記事の内容を象徴する、ブログのアイキャッチ画像のプロンプト（英語）を作成してください。
            未来的で、AI技術を感じさせる、わかりやすい図解のようなスタイルを含めてください。

            記事内容:
            $dialogue
        """.trimIndent()

        val imagePrompt = openAiClient.generateChat("gpt-5-mini-2025-08-07", listOf(ChatMessage("user", imagePromptGenPrompt)))

        // 5. 画像生成
        val imageUrl = openAiClient.generateImage(imagePrompt)

        // 6. 最終的な記事の整形
        val finalContent = """
            # ${targetNews.title}

            ## ニュース要約
            $summary

            ## AI討論会
            $dialogue

            ## 元記事
            [${targetNews.title}](${targetNews.link})

            ---
            ※この記事のアイキャッチ画像はAIによって自動生成されたものです。
            ※画像リンクの有効期限は生成から約1時間です。記事を公開する前に、リンクから画像を保存し、noteにアップロードしてください。
        """.trimIndent()

        return finalContent to imageUrl
    }
}
