import streamlit as st
from PIL import Image, ImageOps
import pillow_heif
import os
import io
import time
from google import genai
from google.genai import types

def generate_furniture_image(api_key, input_image_pil, prompt_text):
    """
    Google Cloud Vertex AI (Gemini Image Preview) を使用して、入力画像に基づいて家具を配置した画像を生成する。
    """

    # プロンプトの組み立て
    full_prompt = (
        f"あなたはプロのインテリアデザイナーです。"
        f"この空室の部屋の写真に、以下のスタイルで家具を配置した画像を生成してください。\n"
        f"スタイル指定: {prompt_text}\n"
        f"部屋のパース(奥行き)や採光に合わせた自然な配置をお願いします。高品質な写真のようにしてください。"
    )

    try:
        # APIキーがない場合はモック画像を返す(ローカルテスト用)
        if not api_key:
            time.sleep(2)
            st.warning("APIキーが設定されていないため、テスト用の白黒モック画像を返します。")
            return input_image_pil.convert('L')

        # Gemini Client の初期化
        client = genai.Client(
            api_key=api_key,
        )

        # ユーザー指定のモデルを使用
        # 画像生成に対応した実験的モデルを指定
        model_name = "gemini-3.1-flash-image-preview"

        # ユーザー提供コードに沿ったGenerateContent設定 (画像生成用)
        generate_content_config = types.GenerateContentConfig(
            temperature = 1,
            top_p = 0.95,
            response_modalities = ["IMAGE"], # 画像を生成するように指定
            safety_settings = [
                types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
                types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
            ],
            # Gemini APIの GenerateContentConfig.image_config は output_mime_type をサポートしていないため削除
            # aspect_ratio 等はモデルによってはサポートされない場合があるため最小構成に
        )

        contents = [
            full_prompt,
            input_image_pil,
        ]

        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=generate_content_config,
        )

        # レスポンスから画像を取得
        if response.candidates and response.candidates[0].content.parts:
            # "IMAGE" モダリティの場合、part.inline_dataに画像が入る
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = part.inline_data.data
                    return Image.open(io.BytesIO(image_bytes))

            st.error("レスポンスに画像データが含まれていませんでした。テキストが返された可能性があります。")
        else:
            st.error("Gemini から画像が返されませんでした。")

        return None

    except Exception as e:
        error_msg = str(e)
        st.error(f"画像生成中にエラーが発生しました: {error_msg}")
        if "403" in error_msg or "API_KEY_INVALID" in error_msg:
             st.error("APIキーが無効です。Google AI Studioで取得した正しいキーを設定してください。")
        elif "404" in error_msg or "models/" in error_msg:
             st.error("指定されたモデルにアクセスできません。")
        return None

# HEICフォーマット(iPhone等の高効率画像)を読み込めるようにする
pillow_heif.register_heif_opener()

def main():
    st.set_page_config(page_title="新築マンション 家具配置シミュレーター (Google Cloud)", layout="wide")
    st.title("🏡 新築マンション 家具配置シミュレーター")
    st.write("家具の入っていないお部屋の写真から、AIが自動で家具を配置したイメージを生成します。")

    # APIキーをセッションステートで管理する
    if 'gemini_api_key' not in st.session_state:
        st.session_state['gemini_api_key'] = os.environ.get("GOOGLE_CLOUD_API_KEY", "")

    # 設定入力
    st.sidebar.header("⚙️ 設定 (Google Cloud)")

    # keyを指定することで自動的にst.session_state['gemini_api_key']と同期し、再起動(リロード)まで維持されます
    st.sidebar.text_input(
        "Google Cloud APIキー:",
        type="password",
        key="gemini_api_key",
        help="Google Cloud Platform で取得したAPIキーを入力してください。一度入力すると、画面を閉じるまで保存されます。"
    )

    current_api_key = st.session_state.get('gemini_api_key', '')

    if not current_api_key:
        st.sidebar.warning("⚠️ テストモード(白黒変換)で動作します")

    st.sidebar.markdown("---")

    # 入力方法の選択
    st.sidebar.header("1. お部屋の写真を用意する")
    input_method = st.sidebar.radio("入力方法を選択:", ("カメラで撮影する", "画像をアップロードする"))

    image_file = None

    if input_method == "カメラで撮影する":
        image_file = st.camera_input("お部屋の写真を撮影してください")
    else:
        # HEICなどの形式も許可
        image_file = st.file_uploader("お部屋の写真をアップロードしてください", type=["jpg", "jpeg", "png", "heic", "heif"])

    # 家具のスタイルの選択
    st.sidebar.header("2. 家具のスタイルを選ぶ")
    styles = {
        "モダン": "モダンでスタイリッシュな家具を配置。白と黒を基調とした直線的なデザイン。",
        "北欧風": "北欧風の温かみのある家具を配置。木目調とパステルカラー、観葉植物。",
        "ヴィンテージ": "ヴィンテージ感のあるレトロな家具を配置。ダークウッドとレザー素材。",
        "ミニマル": "ミニマルで必要最低限の家具のみを配置。空間を広く見せるシンプルなデザイン。"
    }

    style_options = list(styles.keys()) + ["自由にテキストで指定 (1パターン)"]
    selected_style = st.sidebar.radio("スタイルを選択:", style_options)

    prompt = ""
    if selected_style == "自由にテキストで指定 (1パターン)":
        custom_prompt = st.sidebar.text_area("ご希望の家具の雰囲気や種類を入力してください (例: アジアンリゾート風で、大きなソファを置きたい)")
        if custom_prompt:
            prompt = custom_prompt
    else:
        prompt = styles[selected_style]

    st.sidebar.markdown("---")

    # プレビュー
    if image_file is not None:
        try:
            # 画像の読み込みとEXIFの向き情報を適用 (スマホカメラ等の自動回転対応)
            image = Image.open(image_file)
            image = ImageOps.exif_transpose(image)
        except Exception as e:
            st.error(f"画像の読み込みに失敗しました。別の画像をお試しください。({e})")
            return

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("撮影/アップロードした写真 (Before)")

            # 回転オプションをサイドバーではなくメイン画面の画像の近くに配置
            rotation_options = {"回転なし": 0, "右へ90度": -90, "180度": 180, "左へ90度": 90}
            selected_rotation = st.radio("🔄 画像の回転方向を調整:", list(rotation_options.keys()), horizontal=True)

            # 選択された角度で画像を回転 (expand=True で画像が見切れないようにする)
            if rotation_options[selected_rotation] != 0:
                image = image.rotate(rotation_options[selected_rotation], expand=True)

            st.image(image, use_container_width=True)

        with col2:
            st.subheader("家具配置イメージ (After)")
            generate_button = st.button("家具を配置する ✨", type="primary", use_container_width=True)

            if generate_button:
                if not prompt:
                    st.warning("家具のスタイルが指定されていません。テキストを入力するか、固定スタイルを選択してください。")
                else:
                    with st.spinner("Google Gemini を使用して画像を生成中... (数分かかる場合があります)"):
                        generated_image = generate_furniture_image(current_api_key, image, prompt)

                        if generated_image:
                            st.image(generated_image, use_container_width=True)
                            st.success("家具の配置イメージの生成が完了しました！")
                        else:
                            st.error("画像の生成に失敗しました。")

if __name__ == "__main__":
    main()
