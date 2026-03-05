import streamlit as st
from PIL import Image
import os
import io
import time
import base64
import requests
from apify_client import ApifyClient

def get_base64_from_pil(img):
    buffered = io.BytesIO()
    # JPEGとして保存（RGBに変換してアルファチャンネルを削除）
    img = img.convert("RGB")
    img.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def generate_furniture_image(client, input_image_pil, prompt_text):
    """
    Apify の Nano Banana Pro API Actor を使用して、入力画像に基づいて家具を配置した画像を生成する。
    """

    # プロンプトの組み立て
    full_prompt = (
        f"あなたはプロのインテリアデザイナーです。"
        f"この空室の部屋の写真に、以下のスタイルで家具を配置してください。\n"
        f"スタイル指定: {prompt_text}\n"
        f"部屋のパース(奥行き)や採光に合わせた自然な配置をお願いします。"
    )

    try:
        # クライアント(APIキー)がない場合はモック画像を返す(ローカルテスト用)
        if not client:
            time.sleep(2)
            st.warning("APIキーが設定されていないため、テスト用の白黒モック画像を返します。")
            return input_image_pil.convert('L')

        # 1. PIL画像をbase64またはData URIに変換
        base64_image = get_base64_from_pil(input_image_pil)
        image_data_uri = f"data:image/jpeg;base64,{base64_image}"

        # 2. Apify Actorへの入力データを準備
        # Actor: alizarin_refrigerator-owner/nanobanana-pro
        run_input = {
            "prompt": full_prompt,
            # 画像編集 (Image-to-Image) のために参照画像を渡す
            "referenceImage": image_data_uri,
            "demoMode": False
        }

        # 3. Actorを実行して完了を待つ
        run = client.actor("alizarin_refrigerator-owner/nanobanana-pro").call(run_input=run_input)

        # 4. 結果のデータセットから画像URLを取得
        dataset_id = run.get("defaultDatasetId")
        if not dataset_id:
            st.error("APIの実行に失敗しました。Dataset IDが取得できません。")
            return None

        # データセットからアイテムを取得
        items = list(client.dataset(dataset_id).iterate_items())

        if items and len(items) > 0:
            # 最初のアイテムから結果画像のURLを取得 (出力キーはActorの仕様に依存します。一般的には url, outputUrl, image など)
            item = items[0]

            # 可能なキーを順番にチェック
            image_url = None
            for key in ["imageUrl", "url", "outputUrl", "image", "output"]:
                if key in item and isinstance(item[key], str) and item[key].startswith("http"):
                    image_url = item[key]
                    break

            if image_url:
                # 画像URLからデータをダウンロードしてPIL画像にする
                response = requests.get(image_url)
                if response.status_code == 200:
                    return Image.open(io.BytesIO(response.content))
                else:
                    st.error(f"生成された画像のダウンロードに失敗しました (Status Code: {response.status_code})")
            else:
                st.error("APIのレスポンスから画像URLが見つかりませんでした。")
                st.json(item) # デバッグ用に出力
        else:
            st.error("APIから画像が返されませんでした。")

        return None

    except Exception as e:
        st.error(f"画像生成中にエラーが発生しました: {str(e)}")
        return None

def main():
    st.set_page_config(page_title="新築マンション 家具配置シミュレーター (Nano Banana Pro)", layout="wide")
    st.title("🏡 新築マンション 家具配置シミュレーター")
    st.write("家具の入っていないお部屋の写真から、AIが自動で家具を配置したイメージを生成します。")

    # 設定・APIキー入力
    st.sidebar.header("⚙️ 設定 (API連携)")
    # ユーザーが画面から入力したAPIキーを優先。デフォルトは環境変数から取得。
    default_token = os.environ.get("APIFY_API_TOKEN", "")
    api_key_input = st.sidebar.text_input(
        "Nano Banana Pro (Apify) APIキー:",
        value=default_token,
        type="password",
        help="Apifyで取得したAPIトークン(APIFY_API_TOKEN)を入力してください。空欄の場合はテストモード(白黒変換)で動作します。"
    )
    st.sidebar.markdown("---")

    # 入力方法の選択
    st.sidebar.header("1. お部屋の写真を用意する")
    input_method = st.sidebar.radio("入力方法を選択:", ("カメラで撮影する", "画像をアップロードする"))

    image_file = None

    if input_method == "カメラで撮影する":
        image_file = st.camera_input("お部屋の写真を撮影してください")
    else:
        image_file = st.file_uploader("お部屋の写真をアップロードしてください", type=["jpg", "jpeg", "png"])

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
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("撮影/アップロードした写真 (Before)")
            image = Image.open(image_file)
            st.image(image, width='stretch')

        with col2:
            st.subheader("家具配置イメージ (After)")
            generate_button = st.button("家具を配置する ✨", type="primary", use_container_width=True) # NOTE: st.button does not support 'width' parameter yet in this version, so leaving use_container_width

            if generate_button:
                if not prompt:
                    st.warning("家具のスタイルが指定されていません。テキストを入力するか、固定スタイルを選択してください。")
                else:
                    with st.spinner("Nano Banana Pro (Apify) APIを使用して画像を生成中... 処理に数分かかる場合があります。"):
                        # Apify クライアントの初期化 (入力されたAPIキーを使用)
                        if not api_key_input:
                            client = None
                        else:
                            client = ApifyClient(api_key_input)

                        generated_image = generate_furniture_image(client, image, prompt)

                        if generated_image:
                            st.image(generated_image, width='stretch')
                            st.success("家具の配置イメージの生成が完了しました！")
                        else:
                            st.error("画像の生成に失敗しました。")

if __name__ == "__main__":
    main()
