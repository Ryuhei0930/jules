import streamlit as st
import asyncio
import os
import subprocess
from main import fetch_latest_ai_news, generate_blog_content
from note_poster import post_to_note
from dotenv import set_key

st.set_page_config(page_title="AIニュース自動ブログ生成", page_icon="🤖", layout="centered")

@st.cache_resource
def install_playwright():
    """Streamlit Cloud環境でPlaywrightのブラウザをインストールするための関数"""
    try:
        # PlaywrightのChromiumブラウザをインストール
        subprocess.run(["playwright", "install", "chromium"], check=True)
        # ※Streamlit Cloudではsudo権限がないためinstall-depsは実行できません。
        # 必要なシステムパッケージは packages.txt 側でインストールさせます。
        return True
    except Exception as e:
        st.error(f"Playwrightのインストール中にエラーが発生しました: {e}")
        return False

# 初回起動時にPlaywrightをインストール
install_playwright()

def save_env(key, value):
    """環境変数と.envファイルに設定を保存する"""
    os.environ[key] = value
    # .envファイルが存在しない場合は作成する
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('')
    set_key('.env', key, value)

st.title("🤖 AIニュース自動ブログ生成アプリ")
st.markdown("""
このアプリは、最新のAIニュースを自動で取得し、Geminiに「ワイドショーの討論形式」で面白いブログ記事を作成させ、**Note.comへ自動で下書き保存**するシステムです。
""")

with st.sidebar:
    st.header("⚙️ 初期設定")
    with st.form("settings_form"):
        gemini_key = st.text_input("Gemini APIキー", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
        note_email = st.text_input("Note ログインメールアドレス", value=os.environ.get("NOTE_EMAIL", ""))
        note_pass = st.text_input("Note ログインパスワード", value=os.environ.get("NOTE_PASSWORD", ""), type="password")

        submitted = st.form_submit_button("設定を保存")
        if submitted:
            save_env("GEMINI_API_KEY", gemini_key)
            save_env("NOTE_EMAIL", note_email)
            save_env("NOTE_PASSWORD", note_pass)
            st.success("✅ 設定を保存しました。")

st.divider()

if st.button("🚀 今すぐブログを生成してNoteに投稿（下書き）する", type="primary", use_container_width=True):
    # 設定の確認
    if not os.environ.get("GEMINI_API_KEY"):
        st.error("エラー: Gemini APIキーが設定されていません。サイドバーから設定してください。")
        st.stop()
    if not os.environ.get("NOTE_EMAIL") or not os.environ.get("NOTE_PASSWORD"):
        st.error("エラー: Noteのログイン情報が設定されていません。サイドバーから設定してください。")
        st.stop()

    with st.status("自動化処理を実行中...", expanded=True) as status:
        try:
            # 1. RSS取得
            st.write("📡 最新のAIニュースを取得中...")
            news = fetch_latest_ai_news()

            if not news:
                status.update(label="ニュースの取得に失敗しました", state="error")
                st.stop()

            st.write(f"✅ 取得完了: **{news['title']}**")

            # 2. 記事生成
            st.write("🧠 Geminiが白熱討論ブログを執筆中...（約10〜30秒かかります）")
            title, body = generate_blog_content(news)

            if not title or not body:
                status.update(label="記事の生成に失敗しました", state="error")
                st.stop()

            st.write("✅ 記事の生成が完了しました！")

            # プレビュー表示（エキスパンダー内）
            with st.expander("📝 生成された記事のプレビューを確認"):
                st.subheader(title)
                st.markdown(body)

            # 3. Noteへの投稿
            st.write("🌐 Noteへログインし、下書きとして保存中...")
            asyncio.run(post_to_note(title, body))

            status.update(label="全ての処理が完了しました！", state="complete")
            st.balloons()
            st.success("🎉 Note.comの「記事」画面に下書きとして保存されました。確認して手動で公開してください！")

        except Exception as e:
            status.update(label="エラーが発生しました", state="error")
            st.error(f"詳細: {e}")
