import streamlit as st
import os
import sys

# Ensure db module can be imported from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db

st.set_page_config(page_title="システム管理画面", page_icon="⚙️", layout="wide")

# Check if admin is logged in
if "user" not in st.session_state or st.session_state.user["role"] != "admin":
    st.warning("管理者としてログインしてください。")
    if st.button("ログイン画面に戻る"):
        st.switch_page("app.py")
    st.stop()

st.title("⚙️ システム管理画面")

if st.sidebar.button("ログアウト"):
    st.session_state.clear()
    st.switch_page("app.py")

st.sidebar.divider()
st.sidebar.markdown(f"ログイン中: **{st.session_state.user['username']}**")

# --- Tabs ---
tab1, tab2, tab3, tab4 = st.tabs(["APIキー設定", "基本プロンプト設定", "クライアント管理", "利用状況・カウンター"])

with tab1:
    st.header("🔑 Gemini APIキー設定")
    st.markdown("ここで設定したAPIキーが全てのクライアントの画像生成に使用されます。クライアントには表示されません。")
    current_key = db.get_api_key()

    with st.form("api_key_form"):
        new_key = st.text_input("Gemini APIキー", value=current_key, type="password")
        if st.form_submit_button("保存"):
            if new_key:
                db.set_api_key(new_key)
                st.success("APIキーを保存しました。")
            else:
                st.error("APIキーを入力してください。")

with tab2:
    st.header("📝 基本プロンプト設定")
    st.markdown("ここで設定した文章が、全ての画像生成の際に「共通のシステム指示（ベース）」としてAIに渡されます。")
    current_prompt = db.get_base_prompt()

    with st.form("prompt_form"):
        new_prompt = st.text_area("基本プロンプト", value=current_prompt, height=150)
        if st.form_submit_button("設定を保存"):
            db.set_base_prompt(new_prompt)
            st.success("基本プロンプトを更新しました。")

with tab3:
    st.header("👥 クライアントアカウント管理")
    st.info("""
    **【ログインIDの発行方法とクライアントへの案内手順】**
    1. 下記の「新規クライアント追加」を開きます。
    2. 任意の「ログインID」と「パスワード」を入力し、毎月の「生成上限枚数」を設定して「追加」ボタンを押します。
    3. クライアントには、**作成したログインID・パスワード** と **このシステムのURL** をお伝えください。
    ※ クライアント側からパスワードの変更はできないため、管理者が安全に保管・伝達してください。
    """)

    # Add new user
    with st.expander("新規クライアント追加", expanded=False):
        with st.form("add_user_form"):
            new_username = st.text_input("ログインID (半角英数字)")
            new_password = st.text_input("パスワード", type="password")
            new_limit = st.number_input("月間生成上限枚数", min_value=1, value=50, step=10)

            if st.form_submit_button("追加"):
                if new_username and new_password:
                    if db.add_user(new_username, new_password, new_limit):
                        st.success(f"ユーザー '{new_username}' を追加しました。")
                        st.rerun()
                    else:
                        st.error("そのログインIDは既に存在します。")
                else:
                    st.error("IDとパスワードは必須です。")

    st.subheader("登録済みクライアント一覧")
    users = db.get_users()
    if users:
        for user in users:
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            col1.write(f"**ID:** {user['username']}")
            with col2:
                new_lim = st.number_input("上限", min_value=1, value=user['monthly_limit'], key=f"lim_{user['id']}", label_visibility="collapsed")
            with col3:
                if st.button("上限更新", key=f"upd_{user['id']}"):
                    db.update_user_limit(user['id'], new_lim)
                    st.success("更新しました")
                    st.rerun()
            with col4:
                if st.button("削除", key=f"del_{user['id']}", type="primary"):
                    db.delete_user(user['id'])
                    st.success("削除しました")
                    st.rerun()
            st.divider()
    else:
        st.info("登録されているクライアントはいません。")

with tab4:
    st.header("📊 今月のクライアント利用状況")
    usage_data = db.get_all_monthly_usage()

    if usage_data:
        for data in usage_data:
            st.markdown(f"### {data['username']}")
            col1, col2 = st.columns(2)
            col1.metric("今月の生成枚数", f"{data['count']} 枚")
            col2.metric("上限設定", f"{data['monthly_limit']} 枚")
            st.progress(min(data['count'] / data['monthly_limit'], 1.0))
            st.divider()
    else:
        st.info("データがありません。")
