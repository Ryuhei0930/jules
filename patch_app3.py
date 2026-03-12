import re

with open("nanobanana_sales_tool/app.py", "r") as f:
    content = f.read()

search = """    # keyを指定することで自動的にst.session_state['gemini_api_key']と同期し、再起動(リロード)まで維持されます
    st.sidebar.text_input(
        "Google Cloud APIキー:",
        type="password",
        key="gemini_api_key",
        help="Google Cloud Platform で取得したAPIキーを入力してください。一度入力すると、画面を閉じるまで保存されます。"
    )

    current_api_key = st.session_state.get('gemini_api_key', '')

    if not current_api_key:
        st.sidebar.warning("⚠️ テストモード(白黒変換)で動作します")

    st.sidebar.markdown("---")"""

replace = """    # keyを指定することで自動的にst.session_state['gemini_api_key']と同期し、再起動(リロード)まで維持されます
    st.sidebar.text_input(
        "Google Cloud APIキー:",
        type="password",
        key="gemini_api_key",
        help="Google Cloud Platform で取得したAPIキーを入力してください。一度入力すると、画面を閉じるまで保存されます。"
    )

    current_api_key = st.session_state.get('gemini_api_key', '')

    if st.sidebar.button("APIキーを保存・テストする"):
        if current_api_key:
            try:
                # 軽量なモデルでAPIキーの有効性をテスト
                test_client = genai.Client(api_key=current_api_key)
                test_client.models.generate_content(
                    model='gemini-1.5-flash',
                    contents='test'
                )
                st.sidebar.success("✅ APIキーが有効です！保存されました。")
            except Exception as e:
                st.sidebar.error("❌ APIキーが無効か、通信エラーです。正しいキーを確認してください。")
        else:
            st.sidebar.error("キーを入力してください。")

    if not current_api_key:
        st.sidebar.warning("⚠️ テストモード(白黒変換)で動作します")

    st.sidebar.markdown("---")"""

if search in content:
    content = content.replace(search, replace)
    with open("nanobanana_sales_tool/app.py", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Search block not found")
