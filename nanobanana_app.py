import streamlit as st
import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from google import genai
import db
import uuid

# Configuration
st.set_page_config(page_title="ナノバナナ - バーチャル家具配置", page_icon="🍌", layout="centered")

# Initialize database
try:
    db.init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")

# Styling presets
FURNITURE_STYLES = [
    {"name": "モダン", "prompt": "Modern, sleek furniture, minimalist design, neutral colors."},
    {"name": "北欧風", "prompt": "Scandinavian style, light wood furniture, cozy, bright and airy."},
    {"name": "インダストリアル", "prompt": "Industrial style, exposed brick, metal accents, raw wood, leather."},
    {"name": "クラシック", "prompt": "Classic traditional furniture, elegant, rich woods, warm lighting."},
    {"name": "和モダン", "prompt": "Japanese modern style, low furniture, tatami accents, serene and minimal."}
]

def add_watermark(image_bytes: bytes, text: str) -> bytes:
    """Add a watermark to an image."""
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGBA")

        # Create an image for the watermark with an alpha channel
        txt_layer = Image.new('RGBA', image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Determine font size based on image width
        font_size = max(20, image.width // 30)
        try:
            # Use a default font, usually available
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            # Fallback to default, which may not support Japanese well depending on OS
            font = ImageFont.load_default()

        # Add text at the bottom right
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        x = image.width - text_width - 20
        y = image.height - text_height - 20

        # Draw with some opacity (white text with black outline for visibility)
        outline_color = (0, 0, 0, 128)
        text_color = (255, 255, 255, 128)

        # Outline
        for offset in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=outline_color)

        draw.text((x, y), text, font=font, fill=text_color)

        # Combine
        watermarked = Image.alpha_composite(image, txt_layer)

        # Convert back to RGB for saving/displaying
        out_bytes = BytesIO()
        watermarked.convert("RGB").save(out_bytes, format="PNG")
        return out_bytes.getvalue()
    except Exception as e:
        print(f"Watermarking failed: {e}")
        # Return original if watermarking fails
        return image_bytes

def save_image(img_bytes: bytes, folder: str, prefix: str) -> str:
    """Save image to disk and return path."""
    os.makedirs(folder, exist_ok=True)
    filename = f"{prefix}_{uuid.uuid4().hex}.png"
    filepath = os.path.join(folder, filename)
    with open(filepath, "wb") as f:
        f.write(img_bytes)
    return filepath

def format_style_option(index):
    return FURNITURE_STYLES[index]["name"]

# Session State for Authentication
if 'user' not in st.session_state:
    st.session_state.user = None

# --- UI Layout ---

if not st.session_state.user:
    st.title("🍌 ナノバナナ ログイン")
    with st.form("login_form"):
        username = st.text_input("ユーザー名")
        password = st.text_input("パスワード", type="password")
        submitted = st.form_submit_button("ログイン")

        if submitted:
            # Use string value to avoid passing magic mock to hash function in tests
            user = db.get_user(str(username), str(password))
            if user:
                st.session_state.user = dict(user)
                st.rerun()
            else:
                st.error("ユーザー名またはパスワードが間違っています。")
else:
    user = st.session_state.user

    st.title(f"🍌 ナノバナナ - {user['mansion_name']}")

    # Sidebar
    with st.sidebar:
        st.write(f"**ログイン中**: {user['username']}")

        # Quota placeholder
        quota_placeholder = st.empty()
        # Fetch fresh quota from DB
        fresh_user = db.get_user(user['username'])
        used = fresh_user['used_quota']
        quota = fresh_user['monthly_quota']
        quota_placeholder.write(f"📊 利用枠: {used} / {quota} 枚")

        if st.button("ログアウト"):
            st.session_state.user = None
            st.rerun()

    st.write("お部屋の写真をアップロードして、自然に新しい家具を合成します。")

    # Upload & Selection
    uploaded_file = st.file_uploader("お部屋の写真をアップロードしてください (JPEG/PNG)", type=["jpg", "jpeg", "png"])

    selected_style_idx = st.selectbox(
        "家具の雰囲気を選んでください:",
        options=range(len(FURNITURE_STYLES)),
        format_func=format_style_option
    )
    selected_style = FURNITURE_STYLES[selected_style_idx]

    custom_prompt = st.text_input("追加の要望があれば入力してください (例: 青いソファを置いてください)")

    # Generate Button
    if st.button("🪄 家具を合成する", type="primary", use_container_width=True):
        if not uploaded_file:
            st.warning("写真をアップロードしてください。")
            st.stop()

        gemini_api_key = os.environ.get("GEMINI_API_KEY")
        if not gemini_api_key:
            st.error("Gemini APIキーが環境変数に設定されていません。")
            st.stop()

        # Check quota
        if used >= quota:
            st.error("今月の利用枠上限に達しました。")
            st.stop()

        with st.spinner(f"{selected_style['name']}の家具を合成中..."):
            try:
                # Setup GenAI
                client = genai.Client(api_key=gemini_api_key)

                # Prepare prompt
                base_prompt = "You are a professional interior designer and virtual stager. Add furniture to this empty room photo naturally. Make it look photorealistic and respect the lighting and perspective."
                style_prompt = selected_style["prompt"]
                full_prompt = f"{base_prompt} Style: {style_prompt}. {custom_prompt}"

                # Prepare image
                img_data = uploaded_file.getvalue()
                # Create a part dict compatible with google-genai expectations
                image_part = {
                    "inline_data": {
                        "mime_type": uploaded_file.type,
                        "data": img_data
                    }
                }

                # Generate
                response = client.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=[full_prompt, image_part],
                    config={"response_modalities": ["IMAGE"]}
                )

                # Extract image bytes
                generated_img_bytes = None
                if hasattr(response, 'candidates') and response.candidates:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            generated_img_bytes = part.inline_data.data
                            break

                if not generated_img_bytes:
                    st.error("画像が生成されませんでした。")
                    st.stop()

                # Add watermark
                watermarked_bytes = add_watermark(generated_img_bytes, user['mansion_name'])

                # Display result
                st.image(watermarked_bytes, caption=f"合成結果 ({selected_style['name']})", use_container_width=True)

                # Provide download button
                st.download_button(
                    label="📥 画像をダウンロード",
                    data=watermarked_bytes,
                    file_name="nanobanana_staged.png",
                    mime="image/png"
                )

                # Save paths and increment quota
                orig_path = save_image(img_data, "data/images", "orig")
                gen_path = save_image(watermarked_bytes, "data/images", "gen")

                if db.increment_quota(user['id']):
                    db.log_generation(user['id'], full_prompt, orig_path, gen_path)
                    # Update sidebar
                    fresh_user = db.get_user(user['username'])
                    quota_placeholder.write(f"📊 利用枠: {fresh_user['used_quota']} / {fresh_user['monthly_quota']} 枚")
                    st.success("家具の合成が完了しました！利用枠を1消費しました。")
                else:
                    st.warning("画像は生成されましたが、利用枠の更新に失敗しました。")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
