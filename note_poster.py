import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def post_to_note(title, content):
    """
    Playwrightを使用してNote.comにログインし、下書きとして記事を保存する。
    """
    email = os.getenv("NOTE_EMAIL")
    password = os.getenv("NOTE_PASSWORD")

    if not email or not password:
        print("❌ NOTE_EMAILまたはNOTE_PASSWORDが設定されていません。")
        return False

    print("🌐 Note.comにログインし、記事を下書き保存します...")

    async with async_playwright() as p:
        # ヘッドレスモードを有効にして起動
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # ログインページへ移動
            await page.goto("https://note.com/login", wait_until="networkidle")

            # ログインフォームに入力
            await page.fill('input[name="login"]', email)
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"]')

            # ログイン完了を待機 (トップページなどに遷移するのを待つ)
            await page.wait_for_selector('a[href="/new/text"]', timeout=15000)
            print("✅ ログインに成功しました。")

            # 記事作成ページへ移動
            await page.goto("https://note.com/new/text", wait_until="networkidle")

            # タイトルの入力
            title_input = await page.wait_for_selector('.note-editor__title', timeout=10000)
            if title_input:
                await title_input.fill(title)
                print("✅ タイトルを入力しました。")

            # 本文の入力 (エディターの構造に合わせる)
            # noteのエディターはProseMirrorを使用しているため、フォーカスしてキーボード入力するのが確実
            editor_content = await page.wait_for_selector('.ProseMirror', timeout=10000)
            if editor_content:
                await editor_content.click()
                await page.keyboard.insert_text(content)
                print("✅ 本文を入力しました。")

            # 少し待機して自動保存を待つ、あるいは手動で下書き保存ボタンを押す
            await page.wait_for_timeout(3000)
            print("✅ 下書きとして保存完了（自動保存に依存）")

            return True

        except Exception as e:
            print(f"❌ Note.comへの投稿中にエラーが発生しました: {e}")
            return False

        finally:
            await browser.close()

if __name__ == "__main__":
    # テスト実行用
    sample_title = "テスト自動投稿タイトル"
    sample_content = "これはテスト投稿の本文です。\n\n改行もテストします。"

    # 実行にはNOTE_EMAILとNOTE_PASSWORDの環境変数が必要
    asyncio.run(post_to_note(sample_title, sample_content))