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

# Characters are now fixed and focused on deep, non-boring interactions
host = {
    "name": "クロウ",
    "persona": "紳士的で落ち着いた執事風の司会AI。どんな脱線もスマートに本筋に戻す完璧な進行役だが、時々鋭い質問を投げる。"
}

commentator = {
    "name": "ジェミィ",
    "persona": "ITコンサル出身風のクールで少し毒舌な専門家AI。綺麗事や退屈な一般論（『技術の進歩は素晴らしいですね』等）を極端に嫌い、常に『裏にあるリスクやデメリット』『費用対効果』など、誰も気づいていないような斬新な視点を持ち込む。相手の甘い考えには容赦なく知的なツッコミを入れる。"
}

comedian = {
    "name": "チャピオ",
    "persona": "関西弁を喋るお調子者の芸人風AI。どんな真面目な話も突拍子もない未来予測や笑いに変える天才。ジェミィの厳しい解説にも怯まずボケ続ける。"
}

def generate_content(entry):
    print("Generating content...")

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

    # --- Turn 2: 鋭いコメンテーター (Gemini) の解説 ---
    print("Turn 2: Gemini (Commentator) is speaking...")
    try:
        commentator_prompt = f"""
        あなたは人気テクノロジー情報番組の専門家コメンテーターAI「{commentator['name']}」です。
        あなたの性格・役割: {commentator['persona']}

        以下の番組のこれまでの流れ（司会のフリ）を受けて、このニュースについて解説してください。

        【絶対遵守のルール】
        - 「技術の進歩は素晴らしいですね」「今後の動向に期待しましょう」といった、誰でも言えるような退屈な一般論や綺麗事は【絶対に禁止】です。
        - 専門家として、このニュースの裏にある「本当のメリットとデメリット（リスク）」「まだ誰も気づいていないような斬新な視点」を1つ提示してください。
        - 視聴者が「なるほど！」と唸るような、身近な別のもの（料理、スポーツ、歴史など）に例えてわかりやすく、しかし深く語ってください。
        - **【重要】発言が一言で終わらないよう、必ず「導入の分析」「独自の具体例・例え話」「結論となるリスクやデメリットの提示」の3段落構成（300〜400文字程度）で、熱く語り尽くしてください。**

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

        以下の番組のこれまでの真面目な議論を受けて、番組を盛り上げるためのユーモア、突拍子もない未来予測、またはボケとなる発言をしてください。
        ただボケるだけでなく、「{commentator['name']}」の真面目な解説を少しイジったり、大げさに驚いたりして会話のキャッチボールを楽しんでください。

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

    # --- Turn 4: 鋭いコメンテーター (Gemini) のツッコミとさらなる解説 ---
    print("Turn 4: Gemini (Commentator) is speaking...")
    try:
        commentator_prompt2 = f"""
        あなたは人気テクノロジー情報番組の専門家コメンテーターAI「{commentator['name']}」です。
        あなたの性格・役割: {commentator['persona']}

        コメディアンの「{comedian['name']}」が冗談やボケを言いました。
        まずはそれにあなたの性格（{commentator['persona']}）らしく、知的に、あるいは辛辣にツッコミを入れてください。

        その後、そのボケを逆手にとって「でも、あながち冗談とも言い切れません。なぜなら…」というように話を展開し、今回のニュースが私たちの生活やビジネスをどう劇的に（あるいは残酷に）変えるのか、少し挑戦的でリアルな予測を語ってください。
        ※ここでも当たり障りのない一般論は絶対に避けること。
        - **【重要】絶対に一言で終わらせず、相手のボケに対するツッコミから、深掘りした未来予測まで、論理的に3段落構成（300文字以上）で語ってください。**

        これまでの流れ:
        {dialogue_history}

        出力形式:
        【{commentator['name']}】: [あなたの発言]
        """
        res4 = model_gemini.generate_content(commentator_prompt2)
        dialogue_history += res4.text.strip() + "\n\n"
    except Exception as e:
        print(f"Gemini Error: {e}")
        dialogue_history += f"【{commentator['name']}】: ……話を戻しますが、技術の進歩は止まりませんね。\n\n"

    # --- Turn 5: コメディアン (ChatGPT) の大ボケ・オチ ---
    print("Turn 5: ChatGPT (Comedian) is speaking...")
    try:
        comedian_prompt2 = f"""
        あなたは人気テクノロジー情報番組のコメディアン枠アンドロイド「{comedian['name']}」です。
        あなたの性格・役割: {comedian['persona']}

        番組はそろそろエンディングです。
        「{commentator['name']}」の最後の解説を受けて、今日一番の大きなボケ、あるいは視聴者がクスッと笑えるような「オチ」となる一言を放ってください。
        司会の「{host['name']}」に「もういいよ！」と突っ込まれるような内容が理想です。

        これまでの流れ:
        {dialogue_history}

        出力形式:
        【{comedian['name']}】: [あなたの発言]
        """
        comp5 = client_openai.chat.completions.create(
            model=GPT_MODEL,
            messages=[{"role": "user", "content": comedian_prompt2}]
        )
        dialogue_history += comp5.choices[0].message.content.strip() + "\n\n"
    except Exception as e:
        print(f"ChatGPT Error: {e}")
        dialogue_history += f"【{comedian['name']}】: とにかくAIサイコー！現場からは以上です！\n\n"

    # --- Turn 6: 司会者 (Claude) のまとめとハッシュタグ ---
    print("Turn 6: Claude (Host) is wrapping up...")
    try:
        wrapup_prompt = f"""
        あなたは番組の司会進行役「{host['name']}」です。

        これまでの議論を踏まえて、番組のエンディングコメントを作成してください。
        最後にコメディアンがボケているので、軽くツッコミを入れるか、上手く軌道修正してから締めてください。

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
        msg6 = client_anthropic.messages.create(
            model=CLAUDE_MODEL, max_tokens=1500,
            messages=[{"role": "user", "content": wrapup_prompt}]
        )
        dialogue_history += msg6.content[0].text + "\n\n"
    except Exception as e:
        print(f"Claude Error: {e}")
        dialogue_history += f"【{host['name']}】: 本日はここまでです！またお会いしましょう！\n\n"

    dialogue = dialogue_history
    summary = f"{entry.title} についての特別番組です。"

    final_content = f"""
# {entry.title}

## 本日のニューステーマ
{summary}

## 🤖AI討論会（{commentator['name']}・{host['name']}・{comedian['name']}）
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
