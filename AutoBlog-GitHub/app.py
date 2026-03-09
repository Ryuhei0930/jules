import streamlit as st
import asyncio
from main import fetch_rss, generate_content, post_to_note
import os

st.set_page_config(page_title="AutoBlog AI Generator", page_icon="🤖", layout="wide")

st.title("🤖 AI News AutoBlog Generator")
st.markdown("最新のAIニュースを取得し、3つのAIモデル（Gemini, Claude, ChatGPT）の討論形式ブログを自動生成してnoteに下書き保存します。")

# --- セッションステートの初期化 ---
def init_session_state(key, default_val):
    if key not in st.session_state:
        st.session_state[key] = os.getenv(key, default_val)

init_session_state("GEMINI_API_KEY", "")
init_session_state("ANTHROPIC_API_KEY", "")
init_session_state("OPENAI_API_KEY", "")
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
        anthropic_key = st.text_input("Anthropic API Key", value=st.session_state["ANTHROPIC_API_KEY"], type="password")
        openai_key = st.text_input("OpenAI API Key", value=st.session_state["OPENAI_API_KEY"], type="password")

        st.subheader("Note Credentials")
        note_email = st.text_input("Note Email", value=st.session_state["NOTE_EMAIL"])
        note_password = st.text_input("Note Password", value=st.session_state["NOTE_PASSWORD"], type="password")

        st.subheader("RSS Feed")
        rss_url = st.text_input("RSS URL", value=st.session_state["RSS_URL"])

        # 保存ボタン
        submitted = st.form_submit_button("設定を保存")

    if submitted:
        # ボタンが押されたらセッションステートを更新
        st.session_state["GEMINI_API_KEY"] = gemini_key
        st.session_state["ANTHROPIC_API_KEY"] = anthropic_key
        st.session_state["OPENAI_API_KEY"] = openai_key
        st.session_state["NOTE_EMAIL"] = note_email
        st.session_state["NOTE_PASSWORD"] = note_password
        st.session_state["RSS_URL"] = rss_url
        st.success("設定を保存しました！")

# --- 環境変数の更新（実行時用） ---
# main.py の get_config が os.getenv を使うため、session_stateの値をos.environに反映させる
os.environ["GEMINI_API_KEY"] = st.session_state.get("GEMINI_API_KEY", "")
os.environ["ANTHROPIC_API_KEY"] = st.session_state.get("ANTHROPIC_API_KEY", "")
os.environ["OPENAI_API_KEY"] = st.session_state.get("OPENAI_API_KEY", "")
os.environ["NOTE_EMAIL"] = st.session_state.get("NOTE_EMAIL", "")
os.environ["NOTE_PASSWORD"] = st.session_state.get("NOTE_PASSWORD", "")
os.environ["RSS_URL"] = st.session_state.get("RSS_URL", "")

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
