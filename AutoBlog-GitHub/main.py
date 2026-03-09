import os
import feedparser
import requests
import json
import asyncio
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
GEMINI_MODEL = "gemini-3-flash-preview"
CLAUDE_MODEL = "claude-haiku-4-5-20251001"
GPT_MODEL = "gpt-5-mini-2025-08-07"
IMAGE_MODEL = "dall-e-3"

def fetch_rss():
    rss_url = get_config("RSS_URL", "https://feeds.feedburner.com/TechCrunch/")
    print(f"Fetching RSS from {rss_url}...")
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print("No entries found.")
        return None
    return feed.entries[0]

def generate_content(entry):
    print("Generating content...")

    # 1. Gemini Summary
    try:
        gemini_api_key = get_config("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)

        summary_prompt = f"""
        以下のニュース記事を読み、一般の人にもわかるように要約し、さらに高度な技術的補足情報も付け加えてください。

        タイトル: {entry.title}
        概要: {entry.description}
        URL: {entry.link}
        """

        response = model.generate_content(summary_prompt)
        summary = response.text
    except Exception as e:
        print(f"Gemini Error: {e}")
        summary = "要約の生成に失敗しました。"

    # 2. Claude Dialogue
    try:
        anthropic_api_key = get_config("ANTHROPIC_API_KEY")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY is not set")
        client_anthropic = Anthropic(api_key=anthropic_api_key)

        dialogue_prompt = f"""
        あなたはAIニュース解説ブログの編集長です。
        以下のニュース要約を元に、3人のAIキャラクター（Gemini、Claude、ChatGPT）が討論する形式の記事を作成してください。

        キャラクター設定:
        - Gemini: 最新情報に詳しく、検索能力が高い。論理的で少し堅い。
        - Claude: 全体の構成を考え、バランスを取る司会進行役。知的で穏やか。
        - ChatGPT: 創造的でユニークな視点を持つ。ユーモアや画像生成のアイデアを出す。

        ニュース要約:
        {summary}

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
        """

        message = client_anthropic.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=2000,
            messages=[
                {"role": "user", "content": dialogue_prompt}
            ]
        )
        dialogue = message.content[0].text
    except Exception as e:
        print(f"Claude Error: {e}")
        dialogue = "対話の生成に失敗しました。"

    # 3. ChatGPT Image Prompt
    try:
        openai_api_key = get_config("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        client_openai = OpenAI(api_key=openai_api_key)

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
        print(f"ChatGPT Error: {e}")
        image_prompt = "Futuristic AI technology abstract illustration"

    # 4. Generate Image
    image_path = "generated_image.png"
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

## ニュース要約
{summary}

## AI討論会
{dialogue}

## 元記事
[{entry.title}]({entry.link})
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
        except Exception as e:
            print(f"Login failed: {e}")
            await browser.close()
            return

        # Create New Note
        try:
            print("Creating new note...")
            await page.goto("https://note.com/notes/new")

            # Title
            await page.fill('textarea[placeholder="記事タイトル"]', title) # Note often uses textarea for title now

            # Content
            # Note uses a contenteditable div. We need to be careful.
            # Clicking the editor area first
            await page.click('.editor-content')

            # Using keyboard input is safer than JS injection for React/DraftJS editors
            # But for long content it's slow. Let's try clipboard paste simulation or innerText if possible.
            # Simple approach: Type a bit then paste? Or just type.
            # Given the length, let's try to set innerHTML via JS for the specific paragraph block if possible,
            # but Note's structure is complex.
            # Fallback: Type it (might be slow but reliable).
            # Better: Copy to clipboard and paste.

            # For this script, let's just use fill/type on the main editor area if identifiable.
            # Note's editor is tricky. Let's assume a simple text dump for now.
            # await page.keyboard.type(content) # Too slow for long text.

            # JS Injection approach (Safe evaluation)
            # Note's editor handles newlines better if we insert paragraphs or use innerHTML with <br>
            # Simple conversion: \n -> <br>
            safe_content = content.replace("\n", "<br>")

            await page.evaluate("""(content) => {
                const editor = document.querySelector('.editor-content [contenteditable="true"]');
                if (editor) {
                    editor.innerHTML = content;
                    editor.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""", safe_content)

            # Image Upload
            if image_path and os.path.exists(image_path):
                print("Uploading image...")
                # Note usually has an image upload button.
                # We need to find the file input.
                # Often hidden.
                # Standard pattern: click "Add Image" button, then file chooser.
                # Async file chooser handling:
                async with page.expect_file_chooser() as fc_info:
                    # Click the image add button (this selector is hypothetical and needs maintenance)
                    # Note interface changes often.
                    # As a fallback, we might skip image upload if selector fails.
                    # Trying a generic approach for "Image" button in toolbar
                    await page.click('button[aria-label="画像"]')
                file_chooser = await fc_info.value
                await file_chooser.set_files(image_path)
                # Wait for upload
                await page.wait_for_timeout(5000)

            # Save Draft (or Publish)
            print("Saving draft...")
            await page.click('button:has-text("公開設定")')
            await page.click('button:has-text("下書き保存")')

            print("Draft saved successfully.")

        except Exception as e:
            print(f"Posting failed: {e}")
            # Take screenshot for debugging
            await page.screenshot(path="error_screenshot.png")

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
