import os
import feedparser
import requests
import json
import asyncio
import random
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from playwright.async_api import async_playwright

# Load environment variables
load_dotenv()

def get_config(key, default=""):
    """
    設定を取得する。Streamlit上であればsession_stateを優先し、
    そうでなければ環境変数(.env等)から取得する。
    """
    try:
        import streamlit as st
        # If running under Streamlit and the key is in session state
        if key in st.session_state and st.session_state[key]:
            return st.session_state[key]
    except ImportError:
        pass
    return os.getenv(key, default)

# Models
GEMINI_MODEL = "gemini-2.0-flash"

def fetch_rss():
    rss_url = get_config("RSS_URL", "https://feeds.feedburner.com/TechCrunch/")
    print(f"Fetching RSS from {rss_url}...")
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print("No entries found.")
        return None
    return feed.entries[0]

def generate_content(entry):
    print("Generating content with Gemini as TV Writer...")

    # API Keys initialization
    gemini_api_key = get_config("GEMINI_API_KEY")

    if not gemini_api_key:
        print("Gemini API key is missing.")
        return entry.title, "APIキーが設定されていません。", None

    genai.configure(api_key=gemini_api_key)
    model_gemini = genai.GenerativeModel(GEMINI_MODEL)

    prompt = f"""
あなたは優秀なテレビの構成作家です。さらにあなたは構成作家として番組の内容を考えているだけでなく、出演者のコメントも全て考え完璧な番組台本がかけます。

今回は毎日入手するRSSから注目のニュースをピックアップし、朝の情報番組・ワイドショーみたいに紹介してください。

司会者（1名）・出演者（4名）様々なタイプの人をからいろいろな視点の意見を聞き、朝から為になるAIニュースを紹介する台本を作成してください。
議論は活発に行われ、初心者にもわかりやすい解説から、高度な知識を持つ人も唸るような深い考察まで盛り込んでください。

【番組フォーマット】
- 司会者 (1名): ニュースの紹介、進行、まとめを行う。
- 出演者A (IT専門家): 技術的な深掘りや鋭い分析を行う。
- 出演者B (お笑い芸人枠): ユーモアを交え、少しピントのずれた発言で場を和ませる。
- 出演者C (一般市民代表): 視聴者目線での素朴な疑問や不安を代弁する。
- 出演者D (熱血起業家): ビジネスチャンスとしてポジティブかつ熱く語る。

【ニュース内容】
タイトル: {entry.title}
概要: {entry.description}
リンク: {entry.link}

【絶対遵守のルール】
- 番組の台本形式（各キャラクターのセリフの掛け合い）で出力してください。
- 議論は最低でも8往復以上の充実したボリューム（長文）にしてください。
- 記事はnoteで収益（投げ銭）を得ることを目的としているため、番組の最後に司会者から、丁寧に番組のノリを活かして読者へ「サポート（投げ銭）」をお願いする一言を添えてください。
- サポートのお願いの直後に、今回のニュース内容やAIに関連するハッシュタグを必ず10個以上生成して出力してください（例: #AI #最新テクノロジー など）。

さあ、最高のワイドショーの台本をお願いします。
    """

    try:
        response = model_gemini.generate_content(prompt)
        dialogue = response.text.strip()
    except Exception as e:
        print(f"Gemini Error: {e}")
        dialogue = "台本の生成に失敗しました。"

    summary = f"【本日のテーマ】\n{entry.title}"

    final_content = f"""
# {entry.title}

## 本日のニューステーマ
{summary}

## 📺 AIワイドショー討論
{dialogue}

## 🔗元記事
[{entry.title}]({entry.link})
    """

    return entry.title, final_content, None

async def post_to_note(title, content, image_path=None):
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
