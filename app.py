import streamlit as st
import asyncio
import os
import subprocess
from main import fetch_latest_ai_news, generate_blog_content
from note_poster import post_to_note
from dotenv import set_key
from google import genai

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

        submitted = st.form_submit_button("設定を保存してAPIをテスト")
        if submitted:
            # APIキーの有効性テスト
            try:
                if gemini_key:
                    with st.spinner("APIキーを検証中..."):
                        client = genai.Client(api_key=gemini_key)
                        # APIの疎通確認
                        response = client.models.generate_content(
                            model='gemini-3.1-flash-lite-preview',
                            contents='test'
                        )
                # テスト成功時（またはキーが空の時は検証スキップ）
                save_env("GEMINI_API_KEY", gemini_key)
                save_env("NOTE_EMAIL", note_email)
                save_env("NOTE_PASSWORD", note_pass)
                if gemini_key:
                    st.success("✅ APIテスト成功！設定を保存しました。")
                else:
                    st.success("✅ 設定を保存しました。")
            except Exception as e:
                st.error("❌ APIキーが無効、または使用できません。正しいキーを入力してください。")
                st.error(f"詳細: {e}")

st.divider()

st.subheader("📰 ブログ化するニュースの選択")
# セッションステートにニュースリストを保存
if "news_list" not in st.session_state:
    st.session_state.news_list = []

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("🔄 最新のニュースを取得する"):
        with st.spinner("RSSから最新ニュースを取得中..."):
            st.session_state.news_list = fetch_latest_ai_news(limit=5)
            if not st.session_state.news_list:
                st.warning("ニュースの取得に失敗したか、記事がありません。")

if st.session_state.news_list:
    news_titles = [f"{i+1}. {news['title']}" for i, news in enumerate(st.session_state.news_list)]
    selected_title = st.selectbox("ブログ化する記事を選んでください:", options=news_titles)

    # 選択された記事のインデックスを取得
    selected_index = news_titles.index(selected_title)
    selected_news = st.session_state.news_list[selected_index]

    # 概要プレビュー
    with st.expander("📄 記事の概要プレビュー"):
        st.write(selected_news['description'])
        st.markdown(f"[元の記事を読む]({selected_news['link']})")

    st.divider()

    if st.button("🚀 選択したニュースでブログを生成してNoteに投稿", type="primary", use_container_width=True):
        # 設定の確認
        if not os.environ.get("GEMINI_API_KEY"):
            st.error("エラー: Gemini APIキーが設定されていません。サイドバーから設定してください。")
            st.stop()
        if not os.environ.get("NOTE_EMAIL") or not os.environ.get("NOTE_PASSWORD"):
            st.error("エラー: Noteのログイン情報が設定されていません。サイドバーから設定してください。")
            st.stop()

        with st.status("自動化処理を実行中...", expanded=True) as status:
            try:
                # 1. 記事生成
                st.write(f"🧠 Geminiが白熱討論ブログを執筆中...（対象: {selected_news['title']}）")
                try:
                    title, body = generate_blog_content(selected_news)
                    st.write("✅ 記事の生成が完了しました！")
                except Exception as e:
                    status.update(label="❌ 記事の生成中にエラーが発生しました", state="error")
                    st.error(f"詳細エラー内容: {e}")
                    st.warning("APIキーが未設定か間違っている、無料枠の上限に達している、または生成されたニュースがポリシー違反でブロックされた可能性があります。サイドバーの「設定を保存してAPIをテスト」ボタンでAPIキーが有効か確認してください。")
                    st.stop()

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
else:
    st.info("上の「最新のニュースを取得する」ボタンを押して、記事を選んでください。")
