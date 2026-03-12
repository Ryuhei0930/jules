import streamlit as st
import asyncio
from main import fetch_rss, generate_content, post_to_note
import os
import subprocess
import google.generativeai as genai
from dotenv import set_key, find_dotenv

st.set_page_config(page_title="AutoBlog AI Generator", page_icon="🤖", layout="wide")

import os
import subprocess

# --- Playwright Browser Installation for Streamlit Cloud ---
# This must run before any Playwright code is executed.
# We run it synchronously (without @st.cache_resource) so that if the Streamlit container
# is restarted or moved, the browser binary is re-downloaded to ~/.cache/ms-playwright/
# Since the command is idempotent, running it on every startup is safe and very fast if already installed.
import sys

def install_playwright():
    try:
        # Streamlit Cloud uses Debian/Ubuntu. We only need chromium.
        print("Checking/Installing Playwright chromium...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Playwright chromium installed successfully.")
    except Exception as e:
        print(f"Failed to install Playwright chromium: {e}")

install_playwright()

def verify_api_keys(gemini_key):
    results = {}

    # Verify Gemini
    try:
        if gemini_key:
            genai.configure(api_key=gemini_key)
            # Use list_models as it is the safest way to verify an API key without
            # hardcoding a model name that might be deprecated or unavailable.
            list(genai.list_models())
            results["Gemini"] = {"status": "✅ OK", "error": None}
        else:
            results["Gemini"] = {"status": "⚠️ 未入力", "error": None}
    except Exception as e:
        results["Gemini"] = {"status": "❌ エラー", "error": str(e)}

    return results

st.title("🤖 AI News AutoBlog Generator")
st.markdown("最新のAIニュースを取得し、Geminiを使ったワイドショー形式の討論ブログを自動生成してnoteに下書き保存します。")

# --- セッションステートの初期化 ---
def init_session_state(key, default_val):
    if key not in st.session_state:
        st.session_state[key] = os.getenv(key, default_val)

init_session_state("GEMINI_API_KEY", "")
init_session_state("NOTE_EMAIL", "")
init_session_state("NOTE_PASSWORD", "")
init_session_state("RSS_URL", "https://feeds.feedburner.com/TechCrunch/")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定 (Settings)")
    st.markdown("ここで入力した値は、アプリを再起動するまで保持されます。")

    # フォームを使って入力値の反映を明示的な「保存」ボタンに限定する
    with st.form("settings_form"):
        st.subheader("API Keys")
        gemini_key = st.text_input("Gemini API Key", value=st.session_state["GEMINI_API_KEY"], type="password")

        st.subheader("Note Credentials")
        note_email = st.text_input("Note Email", value=st.session_state["NOTE_EMAIL"])
        note_password = st.text_input("Note Password", value=st.session_state["NOTE_PASSWORD"], type="password")

        st.subheader("RSS Feed")
        rss_url = st.text_input("RSS URL", value=st.session_state["RSS_URL"])

        # 保存ボタン
        submitted = st.form_submit_button("設定を保存")

    if submitted:
        # ボタンが押されたらセッションステートと.envファイルを更新
        st.session_state["GEMINI_API_KEY"] = gemini_key
        st.session_state["NOTE_EMAIL"] = note_email
        st.session_state["NOTE_PASSWORD"] = note_password
        st.session_state["RSS_URL"] = rss_url

        # For security reasons on Streamlit Cloud, do not save secrets to local files or env variables
        # as they would be shared with anyone visiting the URL.
        # Instead, secrets are kept only in the user's session state during their active session.
        # In a real environment, you should use Streamlit secrets management for API keys.

        st.success("セッションに設定を保存しました。(アプリを閉じるとリセットされます)")
        st.info("※ Streamlit Cloudは公開アプリであり、複数ユーザーが同じバックエンドを共有するため、セキュリティ上パスワード等はファイルに保存しません。")

    st.markdown("---")
    st.subheader("API接続テスト")
    if st.button("設定されたAPIキーをテストする"):
        with st.spinner("APIキーの有効性を確認中..."):
            validation_results = verify_api_keys(
                st.session_state.get("GEMINI_API_KEY", "")
            )

            for provider, result in validation_results.items():
                if "✅" in result["status"]:
                    st.success(f"{provider}: {result['status']}")
                elif "⚠️" in result["status"]:
                    st.warning(f"{provider}: {result['status']}")
                else:
                    st.error(f"{provider}: {result['status']} ({result['error']})")

# --- メイン実行エリア ---
st.header("🚀 ブログ生成と投稿")

if st.button("今すぐブログを生成＆投稿する", type="primary"):
    # 必須項目のチェック
    if not all([gemini_key, note_email, note_password]):
        st.error("エラー: サイドバーで必要なAPIキーとNoteログイン情報をすべて入力してください。")
    else:
        with st.status("処理を開始します...", expanded=True) as status:
            try:
                # 1. RSS取得
                st.write("📡 RSSから最新ニュースを取得中...")
                entry = fetch_rss()
                if not entry:
                    status.update(label="RSSの取得に失敗しました", state="error")
                    st.stop()
                st.success(f"ニュース取得成功: {entry.title}")

                # 2. コンテンツ生成
                st.write("🧠 AIモデルでコンテンツを生成中 (Gemini, Claude, ChatGPT)...")
                title, content, _ = generate_content(entry)

                if not title or not content:
                    status.update(label="コンテンツ生成に失敗しました", state="error")
                    st.stop()
                st.success("記事の生成が完了しました！")

                # プレビュー表示
                with st.expander("生成された記事のプレビュー", expanded=False):
                    st.markdown(content)

                # 3. Note投稿
                st.write("🌐 Noteに自動ログインして下書き保存中...")
                # Playwrightの非同期処理をStreamlit上で実行
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(post_to_note(title, content))
                loop.close()

                status.update(label="🎉 すべての処理が正常に完了しました！", state="complete")
                st.balloons()

            except Exception as e:
                status.update(label=f"エラーが発生しました: {str(e)}", state="error")
                st.error("処理が中断されました。ログを確認してください。")
