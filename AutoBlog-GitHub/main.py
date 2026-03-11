import os
import feedparser
import requests
import json
import asyncio
import random
from datetime import datetime
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

def get_config(key, default=""):
    return os.getenv(key, default)

# Models

# Models
GEMINI_MODEL = "gemini-2.0-flash"
CLAUDE_MODEL = "claude-3-haiku-20240307"
GPT_MODEL = "gpt-4o-mini"
IMAGE_MODEL = "dall-e-3"

def fetch_rss():
    rss_url = get_config("RSS_URL", "https://feeds.feedburner.com/TechCrunch/")
    print(f"Fetching RSS from {rss_url}...")
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print("No entries found.")
        return None
    return feed.entries[0]

# キャラクター設定（各AIモデルごとに3種類）
HOST_CHARACTERS = [
    {"name": "クロウ", "persona": "知的で穏やかな知能派アンドロイド。番組の進行をスムーズにこなし、時にはゲストの脱線を優しくたしなめる。"},
    {"name": "アンナ", "persona": "元気で明るい女性型AIアナウンサー。視聴者目線で分かりやすい言葉を使い、番組をポップに盛り上げる。"},
    {"name": "マスターC", "persona": "ベテランのニュースキャスター風AI。重厚感のある語り口で、議論の要点を的確にまとめる。"}
]

COMMENTATOR_CHARACTERS = [
    {"name": "ジェミィ", "persona": "データ分析と最新技術に精通した真面目な研究者アンドロイド。常にエビデンスを重視し、少し理屈っぽいが解説は正確。"},
    {"name": "プロフェッサーG", "persona": "気難しいが愛嬌のある老教授AI。専門用語を使いたがるが、聞けば丁寧に解説してくれる技術オタク。"},
    {"name": "レイ", "persona": "冷静沈着で論理的な女性型コメンテーター。感情論を排し、常に客観的で鋭い分析を提供する。"}
]

COMEDIAN_CHARACTERS = [
    {"name": "チャピオ", "persona": "創造的でアイデアマンのコメディアンロボット。人間くさい冗談や突拍子もない未来予測を好んで披露し、よくスベるが憎めない。"},
    {"name": "オマツ", "persona": "関西弁で話すお祭り好きのAI。どんな真面目なニュースも、笑いや日常のドタバタに結びつけて語るムードメーカー。"},
    {"name": "ボルト", "persona": "皮肉屋でちょっとシニカルなロボット。自虐ネタや人間社会の矛盾に対する鋭いツッコミで笑いを取る。"}
]

def generate_content(entry):
    print("Generating content...")

    # 毎回ランダムにキャラクターを選出
    host = random.choice(HOST_CHARACTERS)
    commentator = random.choice(COMMENTATOR_CHARACTERS)
    comedian = random.choice(COMEDIAN_CHARACTERS)

    # API Keys initialization
    gemini_api_key = get_config("GEMINI_API_KEY")
    anthropic_api_key = get_config("ANTHROPIC_API_KEY")
    openai_api_key = get_config("OPENAI_API_KEY")

    if not all([gemini_api_key, anthropic_api_key, openai_api_key]):
        print("API keys are missing.")
        return entry.title, "APIキーが設定されていません。", None

    genai.configure(api_key=gemini_api_key)
    model_gemini = genai.GenerativeModel(GEMINI_MODEL)
    client_anthropic = Anthropic(api_key=anthropic_api_key)
    client_openai = OpenAI(api_key=openai_api_key)

    dialogue_history = ""

    # --- Turn 1: 司会者 (Claude) のオープニングとニュース紹介 ---
    print("Turn 1: Claude (Host) is speaking...")
    try:
        host_prompt = f"""
        あなたは人気テクノロジー情報番組の司会進行役を務めるアンドロイド「{host['name']}」です。
        あなたの性格・役割: {host['persona']}

        以下のニュース記事をテーマに今日の番組をスタートさせ、ニュースの概要を視聴者にわかりやすく紹介してください。
        その後、コメンテーターの「{commentator['name']}」に意見を求めてください。

        ニュースタイトル: {entry.title}
        概要: {entry.description}

        出力形式:
        【{host['name']}】: [あなたの発言]
        """
        msg1 = client_anthropic.messages.create(
            model=CLAUDE_MODEL, max_tokens=1000,
            messages=[{"role": "user", "content": host_prompt}]
        )
        dialogue_history += msg1.content[0].text + "\n\n"
    except Exception as e:
        print(f"Claude Error: {e}")
        dialogue_history += f"【{host['name']}】: 申し訳ありません、メインシステムにエラーが発生しました。\n\n"

    # --- Turn 2: 真面目コメンテーター (Gemini) の解説 ---
    print("Turn 2: Gemini (Commentator) is speaking...")
    try:
        commentator_prompt = f"""
        あなたは人気テクノロジー情報番組の真面目なコメンテーターAI「{commentator['name']}」です。
        あなたの性格・役割: {commentator['persona']}

        以下の番組のこれまでの流れ（司会のフリ）を受けて、このニュースの技術的な深掘りや社会への影響について、専門家として解説してください。

        これまでの流れ:
        {dialogue_history}

        出力形式:
        【{commentator['name']}】: [あなたの発言]
        """
        res2 = model_gemini.generate_content(commentator_prompt)
        dialogue_history += res2.text.strip() + "\n\n"
    except Exception as e:
        print(f"Gemini Error: {e}")
        dialogue_history += f"【{commentator['name']}】: データ分析モジュールに一時的な障害が発生しています。\n\n"

    # --- Turn 3: コメディアン (ChatGPT) のボケ・オチ ---
    print("Turn 3: ChatGPT (Comedian) is speaking...")
    try:
        comedian_prompt = f"""
        あなたは人気テクノロジー情報番組のコメディアン枠アンドロイド「{comedian['name']}」です。
        あなたの性格・役割: {comedian['persona']}

        以下の番組のこれまでの真面目な議論を受けて、番組を盛り上げるためのユーモア、突拍子もない未来予測、またはクスッと笑える「オチ」となる発言をしてください。

        これまでの流れ:
        {dialogue_history}

        出力形式:
        【{comedian['name']}】: [あなたの発言]
        """
        comp3 = client_openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": comedian_prompt}]
        )
        dialogue_history += comp3.choices[0].message.content.strip() + "\n\n"
    except Exception as e:
        print(f"ChatGPT Error: {e}")
        dialogue_history += f"【{comedian['name']}】: おっと、笑い回路がショートしてスベりましたわ！\n\n"

    # --- Turn 4: 司会者 (Claude) のまとめとハッシュタグ ---
    print("Turn 4: Claude (Host) is wrapping up...")
    try:
        wrapup_prompt = f"""
        あなたは番組の司会進行役「{host['name']}」です。

        これまでの議論を踏まえて、番組のエンディングコメントを作成してください。

        これまでの流れ:
        {dialogue_history}

        以下の指示に必ず従ってください:
        1. 議論を綺麗にまとめる。
        2. この記事はnoteで収益（投げ銭）を得ることを目的としているため、丁寧に、しかし番組のノリを活かして読者へ「サポート（投げ銭）」をお願いする一言を添える。
        3. サポートのお願いの直後に、今回のニュース内容やAIに関連するハッシュタグを必ず10個以上生成して出力する（例: #AI #最新テクノロジー など）。

        出力形式:
        【{host['name']}】: [あなたのエンディングコメントとサポートのお願い]

        [ハッシュタグのリスト]
        """
        msg4 = client_anthropic.messages.create(
            model=CLAUDE_MODEL, max_tokens=1500,
            messages=[{"role": "user", "content": wrapup_prompt}]
        )
        dialogue_history += msg4.content[0].text + "\n\n"
    except Exception as e:
        print(f"Claude Error: {e}")
        dialogue_history += f"【{host['name']}】: 本日はここまでです！またお会いしましょう！\n\n"

    dialogue = dialogue_history
    summary = f"{entry.title} についての特別番組です。"

    # 5. ChatGPT Image Prompt & DALL-E Image Generation
    image_prompt = "Futuristic AI technology abstract illustration"
    image_path = "generated_image.png"
    image_url = ""

    print("Turn 5: Generating Image Prompt...")
    try:
        image_prompt_gen_prompt = f"""
        以下のAI討論記事の内容を象徴する、ブログのアイキャッチ画像のプロンプト（英語）を作成してください。
        未来的で、AI技術を感じさせる、わかりやすい図解のようなスタイルを含めてください。

        記事内容:
        {dialogue}
        """

        completion = client_openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "user", "content": image_prompt_gen_prompt}
            ]
        )
        image_prompt = completion.choices[0].message.content
    except Exception as e:
        print(f"ChatGPT Image Prompt Error: {e}")

    # Generate Image
    print("Turn 6: Generating Image via DALL-E 3...")
    try:
        response = client_openai.images.generate(
            model=IMAGE_MODEL,
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # Download Image
        img_data = requests.get(image_url).content
        with open(image_path, 'wb') as handler:
            handler.write(img_data)

    except Exception as e:
        print(f"DALL-E Error: {e}")
        image_path = None

    final_content = f"""
# {entry.title}

## 本日のニューステーマ
{summary}

## 🤖AI討論会（{commentator['name']}・{host['name']}・{comedian['name']}）
{dialogue}

## 🔗元記事
[{entry.title}]({entry.link})

---
※この記事のアイキャッチ画像はAIによって自動生成されたものです。
※自動投稿の制約上、画像はリンクとして表示されています。有効期限があるため表示されない場合があります。
[🎨生成されたアイキャッチ画像を見る]({image_url})
    """

    return entry.title, final_content, image_path

async def post_to_note(title, content, image_path):
    note_email = get_config("NOTE_EMAIL")
    note_password = get_config("NOTE_PASSWORD")
    if not note_email or not note_password:
        print("Note credentials missing.")
        return

    print("Starting Playwright automation for Note...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Login
        try:
            print("Logging in...")
            await page.goto("https://note.com/login")
            await page.fill('input[name="email"]', note_email)
            await page.fill('input[name="password"]', note_password)
            await page.click('button[data-id="login_button"]')

            # Wait for login to complete (check for avatar or home feed)
            await page.wait_for_url("https://note.com/", timeout=10000)
            print("Login successful.")
            await page.screenshot(path="debug_login_success.png")
        except Exception as e:
            print(f"Login failed: {e}")
            await page.screenshot(path="error_login_failed.png")
            await browser.close()
            return

        # Create New Note
        try:
            print("Creating new note...")
            await page.goto("https://note.com/notes/new")
            await page.wait_for_selector('textarea[placeholder="記事タイトル"]', timeout=15000)

            # Title
            print("Entering title...")
            await page.fill('textarea[placeholder="記事タイトル"]', title)

            # Content
            print("Entering content...")
            # Using keyboard.insert_text is much safer for React/DraftJS/ProseMirror editors than JS injection
            # Click the editor to focus it first
            await page.click('.editor-content')
            await page.wait_for_timeout(1000) # Short wait to ensure focus

            # Insert text directly (preserves newlines and triggers React events)
            await page.keyboard.insert_text(content)

            # Note: Image upload via Playwright on note.com is highly unstable due to dynamic DOM changes.
            # We append the image URL to the content instead, which is reliable.
            print("Skipping direct image upload for stability. URL is included in content.")

            # Save Draft
            print("Saving draft...")
            # Note's UI sometimes changes between "公開設定" and just a "公開" button.
            # Usually, there's a draft status indicator or button.
            # If standard flow fails, we can just close the browser and Note autosaves.
            # Let's try to click the publish setting menu, then save draft.
            try:
                await page.click('button:has-text("公開設定")', timeout=5000)
                await page.wait_for_timeout(1000)
                await page.click('button:has-text("下書き保存")', timeout=5000)
                print("Draft explicitly saved.")
            except Exception as btn_e:
                print("Could not find explicit save button. Relying on Note's autosave feature.")
                # Wait a few seconds for autosave to trigger before closing
                await page.wait_for_timeout(5000)

            await page.screenshot(path="debug_post_success.png")

        except Exception as e:
            print(f"Posting failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="error_post_failed.png")

        await browser.close()

if __name__ == "__main__":
    entry = fetch_rss()
    if entry:
        print(f"Title: {entry.title}")
        title, content, image_path = generate_content(entry)
        if title and content:
            asyncio.run(post_to_note(title, content, image_path))
        else:
            print("Content generation failed.")
    else:
        print("RSS Fetch failed.")
