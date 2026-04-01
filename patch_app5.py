import re

with open("nanobanana_sales_tool/app.py", "r") as f:
    content = f.read()

search = """    # APIキーをセッションステートで管理する
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = os.environ.get("GOOGLE_CLOUD_API_KEY", "")"""

replace = """    # APIキーをセッションステートで管理する (固定のキーをデフォルトでセット)
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = "AIzaSyAef093oBQJe3EDb3p7HPaRwhFVmWi4AOI" """

if search in content:
    content = content.replace(search, replace)
    with open("nanobanana_sales_tool/app.py", "w") as f:
        f.write(content)
    print("Patched successfully")
else:
    print("Search block not found")
