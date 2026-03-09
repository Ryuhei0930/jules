import streamlit as st
import asyncio
from main import fetch_rss, generate_content, post_to_note
import os

st.set_page_config(page_title="AutoBlog AI Generator", page_icon="🤖", layout="wide")

st.title("🤖 AI News AutoBlog Generator")
st.markdown("最新のAIニュースを取得し、3つのAIモデル（Gemini, Claude, ChatGPT）の討論形式ブログを自動生成してnoteに下書き保存します。")

# --- サイドバー設定 ---
with st.sidebar:
    st.header("⚙️ 設定 (Settings)")

    st.subheader("API Keys")
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    anthropic_key = st.text_input("Anthropic API Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
    openai_key = st.text_input("OpenAI API Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    grok_key = st.text_input("Grok API Key (Optional)", value=os.getenv("GROK_API_KEY", ""), type="password")

    st.subheader("Note Credentials")
    note_email = st.text_input("Note Email", value=os.getenv("NOTE_EMAIL", ""))
    note_password = st.text_input("Note Password", value=os.getenv("NOTE_PASSWORD", ""), type="password")

    st.subheader("RSS Feed")
    rss_url = st.text_input("RSS URL", value=os.getenv("RSS_URL", "https://feeds.feedburner.com/TechCrunch/"))

# --- 環境変数の更新（実行時用） ---
os.environ["GEMINI_API_KEY"] = gemini_key
os.environ["ANTHROPIC_API_KEY"] = anthropic_key
os.environ["OPENAI_API_KEY"] = openai_key
os.environ["NOTE_EMAIL"] = note_email
os.environ["NOTE_PASSWORD"] = note_password
os.environ["RSS_URL"] = rss_url

# --- メイン実行エリア ---
st.header("🚀 ブログ生成と投稿")

if st.button("今すぐブログを生成＆投稿する", type="primary"):
    # 必須項目のチェック
    if not all([gemini_key, anthropic_key, openai_key, note_email, note_password]):
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
                title, content, image_path = generate_content(entry)

                if not title or not content:
                    status.update(label="コンテンツ生成に失敗しました", state="error")
                    st.stop()
                st.success("記事と画像の生成が完了しました！")

                # プレビュー表示
                with st.expander("生成された記事のプレビュー", expanded=False):
                    st.markdown(content)
                    if image_path and os.path.exists(image_path):
                        st.image(image_path, caption="生成されたアイキャッチ画像")

                # 3. Note投稿
                st.write("🌐 Noteに自動ログインして下書き保存中...")
                # Playwrightの非同期処理をStreamlit上で実行
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(post_to_note(title, content, image_path))
                loop.close()

                status.update(label="🎉 すべての処理が正常に完了しました！", state="complete")
                st.balloons()

            except Exception as e:
                status.update(label=f"エラーが発生しました: {str(e)}", state="error")
                st.error("処理が中断されました。ログを確認してください。")
