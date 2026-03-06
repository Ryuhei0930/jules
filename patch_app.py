import re

with open("nanobanana_sales_tool/app.py", "r") as f:
    content = f.read()

# Remove the st.form and just use st.text_input with `key`
search = """    # 設定入力
    st.sidebar.header("⚙️ 設定 (Google Cloud)")

    with st.sidebar.form(key='api_settings_form'):
        api_key_input = st.text_input(
            "Google Cloud APIキー:",
            value=st.session_state['gemini_api_key'],
            type="password",
            help="Google Cloud Platform で取得したAPIキーを入力してください。"
        )

        submit_api_settings = st.form_submit_button("APIキーを保存する")

        if submit_api_settings:
            st.session_state['gemini_api_key'] = api_key_input
            st.sidebar.success("✅ APIキーを一時保存しました。")

    current_api_key = st.session_state['gemini_api_key']"""

replace = """    # 設定入力
    st.sidebar.header("⚙️ 設定 (Google Cloud)")

    # keyを指定することで自動的にst.session_state['gemini_api_key']と同期し、再起動(リロード)まで維持されます
    st.sidebar.text_input(
        "Google Cloud APIキー:",
        type="password",
        key="gemini_api_key",
        help="Google Cloud Platform で取得したAPIキーを入力してください。一度入力すると、画面を閉じるまで保存されます。"
    )

    current_api_key = st.session_state.get('gemini_api_key', '')"""

if search in content:
    content = content.replace(search, replace)
    with open("nanobanana_sales_tool/app.py", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Search block not found")
