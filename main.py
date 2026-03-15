import os
import feedparser
from dotenv import load_dotenv
from google import genai

load_dotenv()

def fetch_latest_ai_news(limit_per_feed=3):
    """
    複数のRSS URLから最新の記事を取得する。
    """
    rss_sources = {
        "Google News AI": "https://news.google.com/rss/search?q=AI+when:1d&hl=ja&gl=JP&ceid=JP:ja",
        "ITmedia AI+": "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
        "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
        "The Verge AI": "https://www.theverge.com/rss/index.xml",
        "WIRED AI": "https://www.wired.com/feed/category/business/latest/rss",
        "TechCrunch": "https://feeds.feedburner.com/TechCrunch/"
    }

    news_list = []

    for source_name, rss_url in rss_sources.items():
        print(f"📡 {source_name} のRSSフィードを取得中: {rss_url}")
        try:
            feed = feedparser.parse(rss_url)
            if not feed.entries:
                print(f"❌ {source_name} のニュース記事が見つかりませんでした。")
                continue

            for entry in feed.entries[:limit_per_feed]:
                title = entry.get('title', 'No Title')
                link = entry.get('link', '')
                description = entry.get('summary', entry.get('description', 'No Description'))

                news_list.append({
                    "source": source_name,
                    "title": title,
                    "link": link,
                    "description": description
                })
        except Exception as e:
            print(f"❌ {source_name} の取得中にエラーが発生しました: {e}")

    print(f"✅ 合計で {len(news_list)} 件の最新ニュースを取得しました。")
    return news_list

def generate_blog_content(news_entry):
    """
    Geminiを使用して、ニュース記事からワイドショー形式のブログ記事を生成する。
    1つのプロンプトでGeminiに複数人のキャラを演じさせることで、APIを統一し安定させる。
    """
    # os.environから最新のキーを取得する
    gemini_key = os.environ.get("GEMINI_API_KEY")
    if not gemini_key:
        raise ValueError("GEMINI_API_KEYが設定されていません。")

    print("🧠 Geminiによるブログ記事生成を開始します...")
    client = genai.Client(api_key=gemini_key)

    prompt = f"""
    あなたはプロのTV番組構成作家であり、大人気のAI解説ブログの執筆者です。
    以下のニュース記事を元に、**「AIニュース深掘り討論！」という架空のワイドショー番組**の書き起こし形式で、ブログ記事を作成してください。

    【ニュース内容】
    タイトル: {news_entry['title']}
    リンク: {news_entry['link']}
    概要: {news_entry['description']}

    【登場人物（すべてあなたが演じ分けてください）】
    🎙️ **MC（司会）**: 進行役。読者目線でわかりやすく質問を投げかける。
    🤖 **Gemini先生**: Google出身のAIコメンテーター。最新の技術トレンドに明るく、論理的で分かりやすい解説が得意。
    🧠 **Claude博士**: Anthropic出身のAI研究者。倫理観が強く、深い洞察と長文での丁寧な解説が得意。プロ向けの情報を提供する。
    💬 **ChatGPT先輩**: OpenAI出身のベテランAI。ユーモアがあり、実用的な活用方法やビジネス目線でのコメントが得意。
    🐶 **Grokアニキ**: X(旧Twitter)出身の反逆児AI。皮肉屋だが核心を突く発言が多く、SNSのトレンドや忖度なしのリアルな意見が得意。

    【記事の構成要件】
    1. **キャッチーなブログタイトル**: (番組名ではなく、ニュースの内容が魅力的に伝わるブログのタイトルを一つ作成し、一番最初の行に `# ` をつけて出力してください)
    2. **番組オープニング**: MCによるニュースの分かりやすい要約（初心者向け）。
    3. **白熱討論パート**:
       - Gemini、Claude、ChatGPT、Grokの4名が、それぞれの個性を活かしてニュースの背景、技術的影響、未来への展望を議論する。
       - 初心者が「なるほど！」と思える図解的な表現や例え話を入れること。
       - 同時に、AIに詳しい玄人が読んでも「深い！」と唸るような専門的な見解（Claude博士の担当など）も必ず含めること。
    4. **エンディングと投げ銭のお願い**:
       - MCが議論を綺麗にまとめる。
       - 最後に、**必ず**「この記事が面白かったら、API代の足しにするため投げ銭（サポート）をお願いします！」という旨のユーモアのあるお願い文を入れること。
    5. **ハッシュタグ**: 最後にnote用のハッシュタグを10個以上つけること。(例: #AI #ニュース #ChatGPT ...)

    【出力形式】
    すべてMarkdown形式で出力してください。見やすく装飾（太字、引用など）を活用してください。
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-lite-preview',
            contents=prompt
        )
        content = response.text
        if not content:
            raise ValueError("Gemini APIからの返答が空でした。ニュース内容が不適切と判定され、ブロックされた可能性があります。")

        # タイトルと本文を分離する
        lines = content.split('\n')
        title = "AIニュース自動生成ブログ"
        body_lines = []

        for line in lines:
            if line.startswith('# ') and title == "AIニュース自動生成ブログ":
                title = line.replace('# ', '').strip()
            else:
                body_lines.append(line)

        body = '\n'.join(body_lines).strip()

        # 最後に元記事のリンクを付与
        body += f"\n\n---\n\n**📰 元のニュース記事はこちら:**\n[{news_entry['title']}]({news_entry['link']}) ({news_entry.get('source', '不明')})"
        print("✅ ブログ記事の生成が完了しました。")
        return title, body

    except Exception as e:
        print(f"❌ Gemini API実行中にエラーが発生しました: {e}")
        # Webアプリ側でエラー原因を表示できるように例外を再送出する
        raise e

if __name__ == "__main__":
    import asyncio
    from note_poster import post_to_note

    # 自動化スクリプト(GitHub Actionsなど)の場合は常に1件目を使用する
    news_list = fetch_latest_ai_news(limit_per_feed=1)
    if news_list:
        news = news_list[0]
        title, body = generate_blog_content(news)
        if title and body:
            print(f"\n--- Title ---\n{title}\n")
            print(f"--- Body ---\n{body[:500]}...\n(省略されました)")

            print("\n📝 Noteへ記事を投稿します...")
            asyncio.run(post_to_note(title, body))
        else:
            print("❌ 記事の生成に失敗したため、投稿を中止します。")