import asyncio
import os
from playwright.async_api import async_playwright
from dotenv import load_dotenv

load_dotenv()

async def post_to_note(title, content):
    """
    Playwrightを使用してNote.comにログインし、下書きとして記事を保存する。
    """
    # os.environから最新の設定を取得する
    email = os.environ.get("NOTE_EMAIL")
    password = os.environ.get("NOTE_PASSWORD")

    if not email or not password:
        raise ValueError("NOTE_EMAILまたはNOTE_PASSWORDが設定されていません。")

    print("🌐 Note.comにログインし、記事を下書き保存します...")

    async with async_playwright() as p:
        # ヘッドレスモードを有効にして起動
        browser = await p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
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
            try:
                # ログイン後のマイページまたはダッシュボードへの遷移を待つ
                await page.wait_for_url("**/note.com**", timeout=15000)
                # 投稿ボタン(要素)が出るか確認
                await page.wait_for_selector('a[href="/new/text"]', timeout=10000)
                print("✅ ログインに成功しました。")
            except Exception as login_err:
                # ログイン失敗時はスクリーンショットを保存
                await page.screenshot(path="login_error.png")
                raise Exception(f"Noteへのログインに失敗しました（パスワード間違いか、Bot対策(reCAPTCHA等)に引っかかっている可能性があります）。詳細はスクリーンショット(login_error.png)を確認してください: {login_err}")

            # 記事作成ページへ移動
            await page.goto("https://note.com/new/text", wait_until="networkidle")

            # タイトルの入力
            try:
                title_input = await page.wait_for_selector('textarea[placeholder="記事タイトル"]', timeout=10000)
                if not title_input:
                    title_input = await page.wait_for_selector('.note-editor__title', timeout=5000)
                await title_input.fill(title)
                print("✅ タイトルを入力しました。")
            except Exception as title_err:
                await page.screenshot(path="title_error.png")
                raise Exception(f"タイトルの入力欄が見つかりませんでした: {title_err}")

            # 本文の入力 (エディターの構造に合わせる)
            try:
                editor_content = await page.wait_for_selector('.ProseMirror', timeout=10000)
                await editor_content.click()
                await page.keyboard.insert_text(content)
                print("✅ 本文を入力しました。")
            except Exception as body_err:
                await page.screenshot(path="body_error.png")
                raise Exception(f"本文の入力欄(ProseMirror)が見つかりませんでした: {body_err}")

            # 少し待機して自動保存を待つ
            await page.wait_for_timeout(3000)
            print("✅ 下書きとして保存完了（自動保存に依存）")

            return True

        except Exception as e:
            # アプリ側でエラーを表示させるために例外を再送出する
            raise e

        finally:
            await browser.close()

if __name__ == "__main__":
    # テスト実行用
    sample_title = "テスト自動投稿タイトル"
    sample_content = "これはテスト投稿の本文です。\n\n改行もテストします。"

    # 実行にはNOTE_EMAILとNOTE_PASSWORDの環境変数が必要
    asyncio.run(post_to_note(sample_title, sample_content))