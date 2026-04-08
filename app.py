import streamlit as st
import os
from google import genai
from PIL import Image
import io
from PIL import ImageDraw, ImageFont
import datetime
import db

st.set_page_config(page_title="バーチャル家具配置ツール", page_icon="🛋️", layout="centered")

# Ensure image directory exists
IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "images")
os.makedirs(IMAGE_DIR, exist_ok=True)

def add_watermark(pil_image, text):
    """Adds a semi-transparent watermark to the generated image to prevent misuse."""
    try:
        img = pil_image.convert("RGBA")
        txt_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_img)

        # Calculate font size based on image width
        font_size = max(int(img.width / 30), 20)
        try:
            # Try to load a Japanese font, fallback to default
            font = ImageFont.truetype("/usr/share/fonts/truetype/fonts-japanese-gothic.ttf", font_size)
        except IOError:
            try:
                # Common path for Japanese fonts on some Linux distros
                font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", font_size)
            except IOError:
                # Ultimate fallback
                font = ImageFont.load_default()

        # Calculate text width/height to center at bottom
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        # Position at bottom right with some padding
        padding = 20
        x = img.width - text_width - padding
        y = img.height - text_height - padding

        # Add a slightly transparent black rectangle background for readability
        bg_padding = 10
        draw.rectangle(
            [x - bg_padding, y - bg_padding, x + text_width + bg_padding, y + text_height + bg_padding],
            fill=(0, 0, 0, 150) # Black with ~60% opacity
        )

        # Draw white text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

        # Composite the images
        watermarked = Image.alpha_composite(img, txt_img)

        # Convert back to RGB for saving/displaying
        return watermarked.convert("RGB")
    except Exception as e:
        # If watermarking fails for any reason, return original to prevent app crash
        print(f"Watermarking failed: {e}")
        return pil_image

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
            st.session_state.user = {
                "id": user["id"],
                "username": username,
                "role": user["role"],
                "mansion_name": user.get("mansion_name")
            }
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
mansion_name = st.session_state.user.get('mansion_name')
title_prefix = f"【{mansion_name}】専用 " if mansion_name else ""

st.title(f"🛋️ {title_prefix}バーチャル家具配置ツール")

# Sidebar: Usage Counter and Logout
with st.sidebar:
    st.header("📊 ご利用状況")

    # Use empty containers so we can update them without a full rerun
    metric_container = st.empty()
    progress_container = st.empty()
    error_container = st.empty()

    def update_sidebar_counters():
        count, limit = db.get_user_monthly_usage(st.session_state.user["id"])
        metric_container.metric("今月の生成枚数", f"{count} / {limit} 枚")
        if limit > 0:
            progress_container.progress(min(count / limit, 1.0))
        if count >= limit:
            error_container.error("⚠️ 今月の上限枚数に達しました。")
        return count, limit

    # Initial draw
    count, limit = update_sidebar_counters()

    st.divider()
    st.markdown(f"ログイン中: **{st.session_state.user['username']}**")
    if st.button("ログアウト"):
        st.session_state.clear()
        st.rerun()

# Main Functionality
st.markdown("お部屋の写真に、AIが自動で家具を配置（バーチャルステージング）します。")

input_method = st.radio("写真の入力方法を選択してください", ("ファイルアップロード", "カメラで撮影"))

uploaded_file = None
if input_method == "ファイルアップロード":
    uploaded_file = st.file_uploader("お部屋の写真をアップロードしてください (JPG/PNG)", type=["jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("カメラで部屋を撮影してください")

style_options = {
    "モダン": "モダンで洗練された家具、すっきりとしたライン、落ち着いた色合い。",
    "北欧風": "北欧スタイルの家具、明るく居心地が良い、明るい木目、ミニマリスト。",
    "インダストリアル": "インダストリアルスタイル、レンガ打ちっぱなし、金属と木の家具、無骨な雰囲気。",
    "自由入力": ""
}

selected_style_name = st.selectbox("家具のスタイルを選択してください", list(style_options.keys()))

custom_prompt = ""
if selected_style_name == "自由入力":
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
        base_prompt = db.get_base_prompt()
        if selected_style_name == "自由入力":
            if not custom_prompt:
                st.warning("自由入力の場合は、イメージを入力してください。")
                st.stop()
            final_prompt = f"{base_prompt}\n\n追加する家具のスタイル・イメージ: {custom_prompt}"
        else:
            final_prompt = f"{base_prompt}\n\n追加する家具のスタイル・イメージ: {style_options[selected_style_name]}"

        with st.status("AIが画像を生成中...", expanded=True) as status:
            try:
                # Load image
                image = Image.open(uploaded_file)

                # Call Gemini
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-3.1-flash-image-preview',
                    contents=[final_prompt, image],
                    config=genai.types.GenerateContentConfig(
                         response_modalities=["IMAGE"],
                    )
                )

                if hasattr(response, "candidates") and response.candidates and hasattr(response.candidates[0], "content") and response.candidates[0].content.parts:
                    # Look for the generated image part
                    generated_image_bytes = None
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, "inline_data") and part.inline_data:
                            generated_image_bytes = part.inline_data.data
                            break

                    if not generated_image_bytes:
                        status.update(label="画像が生成されませんでした。", state="error")
                        st.error("AIからのレスポンスに画像データが含まれていませんでした。")
                        st.stop()

                    # Convert to PIL Image for watermarking
                    pil_img = Image.open(io.BytesIO(generated_image_bytes))

                    # Apply watermark
                    watermark_text = f"【{mansion_name}】専用作成" if mansion_name else "Sample"
                    watermarked_image = add_watermark(pil_img, watermark_text)

                    # Save images locally for admin reporting
                    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    username = st.session_state.user["username"]

                    orig_filename = f"{username}_{timestamp_str}_orig.jpg"
                    orig_filepath = os.path.join(IMAGE_DIR, orig_filename)
                    image.convert("RGB").save(orig_filepath, "JPEG")

                    gen_filename = f"{username}_{timestamp_str}_gen.jpg"
                    gen_filepath = os.path.join(IMAGE_DIR, gen_filename)
                    watermarked_image.convert("RGB").save(gen_filepath, "JPEG", quality=95)

                    # Log generation with paths and prompt
                    # We store paths relative to the project root
                    db.log_generation(
                        user_id=st.session_state.user["id"],
                        prompt=final_prompt,
                        original_image_path=os.path.join("data", "images", orig_filename),
                        generated_image_path=os.path.join("data", "images", gen_filename)
                    )

                    status.update(label="生成が完了しました！", state="complete")
                    st.image(watermarked_image, caption="AIが配置した家具", use_column_width=True)
                    st.success("画像の生成に成功しました。")
                    # Update sidebar counters dynamically without a full rerun
                    update_sidebar_counters()
                else:
                    status.update(label="画像が生成されませんでした。", state="error")
                    st.error("AIからの画像レスポンスが空でした。")

            except Exception as e:
                status.update(label="エラーが発生しました", state="error")
                st.error(f"詳細: {e}")
