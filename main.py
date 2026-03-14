import os
import feedparser
from dotenv import load_dotenv

load_dotenv()

def fetch_latest_ai_news(rss_url="https://feeds.feedburner.com/TechCrunch/"):
    """
    指定されたRSS URLから最新の記事を1件取得する。
    デフォルトはTechCrunch(英語)。日本語のAIニュースソースも検討可。
    """
    print(f"📡 RSSフィードを取得中: {rss_url}")
    feed = feedparser.parse(rss_url)

    if not feed.entries:
        print("❌ ニュース記事が見つかりませんでした。")
        return None

    latest_entry = feed.entries[0]
    title = latest_entry.get('title', 'No Title')
    link = latest_entry.get('link', '')
    description = latest_entry.get('summary', latest_entry.get('description', 'No Description'))

    print(f"✅ 最新ニュースを取得しました: {title}")
    return {
        "title": title,
        "link": link,
        "description": description
    }

from google import genai

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
            model='gemini-1.5-flash',
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
        print("✅ ブログ記事の生成が完了しました。")
        return title, body

    except Exception as e:
        print(f"❌ Gemini API実行中にエラーが発生しました: {e}")
        # Webアプリ側でエラー原因を表示できるように例外を再送出する
        raise e

if __name__ == "__main__":
    import asyncio
    from note_poster import post_to_note

    news = fetch_latest_ai_news()
    if news:
        title, body = generate_blog_content(news)
        if title and body:
            print(f"\n--- Title ---\n{title}\n")
            print(f"--- Body ---\n{body[:500]}...\n(省略されました)")

            print("\n📝 Noteへ記事を投稿します...")
            asyncio.run(post_to_note(title, body))
        else:
            print("❌ 記事の生成に失敗したため、投稿を中止します。")