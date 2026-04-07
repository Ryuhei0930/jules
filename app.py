import streamlit as st
import os
from google import genai
from PIL import Image
import io
import db

st.set_page_config(page_title="バーチャル家具配置ツール", page_icon="🛋️", layout="centered")

# Initialize DB on first run
db.init_db()

# Session State Initialization
if "user" not in st.session_state:
    st.session_state.user = None

# --- Login Logic ---
if st.session_state.user is None:
    st.title("🛋️ バーチャル家具配置ツール")
    st.subheader("ログイン")

    username = st.text_input("ログインID")
    password = st.text_input("パスワード", type="password")

    if st.button("ログイン"):
        user = db.authenticate(username, password)
        if user:
            st.session_state.user = {"id": user["id"], "username": username, "role": user["role"]}
            st.success("ログインに成功しました。")
            st.rerun()
        else:
            st.error("IDまたはパスワードが間違っています。")
    st.stop()

# --- Admin Redirect ---
if st.session_state.user["role"] == "admin":
    st.success("管理者としてログインしました。システム管理画面に移動します。")
    if st.button("システム管理画面へ"):
        st.switch_page("pages/admin.py")
    st.stop()

# --- Client Dashboard ---
st.title("🛋️ バーチャル家具配置ツール")

# Sidebar: Usage Counter and Logout
with st.sidebar:
    st.header("📊 ご利用状況")
    count, limit = db.get_user_monthly_usage(st.session_state.user["id"])

    st.metric("今月の生成枚数", f"{count} / {limit} 枚")
    if limit > 0:
        st.progress(min(count / limit, 1.0))

    if count >= limit:
        st.error("⚠️ 今月の上限枚数に達しました。")

    st.divider()
    st.markdown(f"ログイン中: **{st.session_state.user['username']}**")
    if st.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

# Main Functionality
st.markdown("お部屋の写真に、AIが自動で家具を配置（バーチャルステージング）します。")

uploaded_file = st.file_uploader("お部屋の写真をアップロードしてください (JPG/PNG)", type=["jpg", "jpeg", "png"])

style_options = {
    "モダン (Modern)": "Modern and sleek furniture, clean lines, neutral colors.",
    "北欧風 (Nordic)": "Nordic style furniture, bright, cozy, light wood, minimalist.",
    "インダストリアル (Industrial)": "Industrial style, exposed brick, metal and wood furniture, raw.",
    "自由入力 (Free Text)": ""
}

selected_style_name = st.selectbox("家具のスタイルを選択してください", list(style_options.keys()))

custom_prompt = ""
if selected_style_name == "自由入力 (Free Text)":
    custom_prompt = st.text_area("配置したい家具のイメージを入力してください")

if uploaded_file is not None:
    st.image(uploaded_file, caption="アップロードされた写真", use_column_width=True)

    if st.button("家具を配置する (画像を生成)", type="primary"):
        # Check limit
        if count >= limit:
            st.error("今月の生成上限に達しているため、生成できません。管理者に連絡してください。")
            st.stop()

        # Check API Key
        api_key = db.get_api_key()
        if not api_key:
            st.error("システムエラー: 管理者によるAPIキーの設定が完了していません。")
            st.stop()

        # Determine prompt
        if selected_style_name == "自由入力 (Free Text)":
            if not custom_prompt:
                st.warning("自由入力の場合は、イメージを入力してください。")
                st.stop()
            prompt = f"Add {custom_prompt} to this empty room naturally. Maintain original perspective and lighting."
        else:
            prompt = f"Add {style_options[selected_style_name]} to this empty room naturally. Maintain original perspective and lighting."

        with st.status("AIが画像を生成中...", expanded=True) as status:
            try:
                # Load image
                image = Image.open(uploaded_file)

                # Call Gemini
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.1-flash-image-preview',
                    contents=[prompt, image],
                    config=genai.types.GenerateContentConfig(
                         response_modalities=["IMAGE"],
                    )
                )

                if response.generated_images:
                    generated_image = response.generated_images[0].image

                    # Log generation
                    db.log_generation(st.session_state.user["id"])

                    status.update(label="生成が完了しました！", state="complete")
                    st.image(generated_image, caption="AIが配置した家具", use_column_width=True)
                    st.success("画像の生成に成功しました。左サイドバーのカウンターが更新されました。")
                else:
                    status.update(label="画像が生成されませんでした。", state="error")
                    st.error("AIからの画像レスポンスが空でした。")

            except Exception as e:
                status.update(label="エラーが発生しました", state="error")
                st.error(f"詳細: {e}")
