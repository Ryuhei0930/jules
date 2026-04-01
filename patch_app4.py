import re

with open("nanobanana_sales_tool/app.py", "r") as f:
    content = f.read()

search = """    if st.sidebar.button("APIキーを保存・テストする"):
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
            st.sidebar.error("キーを入力してください。")"""

replace = """    if st.sidebar.button("APIキーを保存・テストする"):
        if current_api_key:
            try:
                # Google AI Studioのキーの場合はモデルリスト取得で検証する(課金や通信エラーを避けるため)
                test_client = genai.Client(api_key=current_api_key)
                # content生成ではなく、単にモデル一覧が取得できるかでキーの有効性をテストする
                list(test_client.models.list())
                st.sidebar.success("✅ APIキーが有効です！保存されました。")
            except Exception as e:
                # ユーザーがAI Studioのキーを使っている場合、エラー詳細を表示する
                st.sidebar.error(f"❌ 通信エラー ({str(e)})")
        else:
            st.sidebar.error("キーを入力してください。")"""

if search in content:
    content = content.replace(search, replace)
    with open("nanobanana_sales_tool/app.py", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Search block not found")
