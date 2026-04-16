import streamlit as st
import pandas as pd
from google import genai
import os

st.set_page_config(page_title="アンケートレポート自動生成", page_icon="📊", layout="wide")

def main():
    st.title("📊 新築分譲マンション アンケートレポート自動生成")
    st.markdown("""
    来場者・資料請求者・購入者のアンケートデータ(CSV)をアップロードすると、
    データに基づく分析レポート、ペルソナ、カスタマージャーニー、ペルソナ画像を自動生成します。
    """)

    with st.sidebar:
        st.header("⚙️ 設定")
        api_key = st.text_input("Gemini APIキー", value=os.environ.get("GEMINI_API_KEY", ""), type="password", key="gemini_api_key_input")
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key

    st.subheader("1. CSVデータのアップロード")
    uploaded_file = st.file_uploader("アンケートデータ（CSV）をアップロードしてください", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            st.success("CSVデータの読み込みに成功しました！")
            with st.expander("データのプレビュー"):
                st.dataframe(df.head())

            # データを文字列に変換（LLMプロンプト用）
            csv_data_str = df.to_csv(index=False)

            st.subheader("2. レポートの生成")
            if st.button("レポートとペルソナ画像を生成", type="primary"):
                if not api_key:
                    st.error("サイドバーでGemini APIキーを設定してください。")
                    return

                try:
                    with st.spinner("データ分析とレポート生成中...（これには数分かかる場合があります）"):
                        client = genai.Client(api_key=api_key)

                        prompt = f"""
以下のCSVデータは、新築分譲マンションの来場者・資料請求者・購入者のアンケートデータです。
このデータを分析し、クライアントに提出できるプロフェッショナルなレベルのレポートを作成してください。

ただのデータの羅列ではなく、データに基づいた考察（コメント）を必ず入れてください。
また、出力は以下の構成でMarkdown形式で出力してください。

1. **データ抽出・分析結果**: データの傾向、重要なインサイト、データに基づく考察
2. **今後の戦略・アクションプラン**: 分析結果を踏まえ、今後どのようにすべきかの提案
3. **ターゲットペルソナ設定**: データから導き出される代表的な顧客ペルソナ（年齢、職業、家族構成、年収、趣味嗜好、抱えている課題など）
4. **カスタマージャーニー**: 認知から購入に至るまでの検討プロセスと各フェーズでのタッチポイント・心理

【アンケートデータ（CSV形式）】
{csv_data_str}
"""
                        response = client.models.generate_content(
                            model='gemini-3.1-flash-lite-preview',
                            contents=prompt,
                        )
                        report_text = response.text
                        st.session_state["report_text"] = report_text
                        st.success("レポートの生成が完了しました！")

                    with st.spinner("ペルソナ画像を生成中..."):
                        # ペルソナ情報から画像生成プロンプトを作成
                        image_prompt_request = f"""
以下のレポートから「ターゲットペルソナ設定」の情報を抽出し、
そのペルソナを描写する画像生成AI（MidjourneyやDALL-Eなど）向けの英語プロンプトを1つ作成してください。
出力は英語のプロンプトのテキストのみにしてください。

【レポート】
{report_text}
"""
                        image_prompt_response = client.models.generate_content(
                            model='gemini-3.1-flash-lite-preview',
                            contents=image_prompt_request,
                        )
                        english_image_prompt = image_prompt_response.text.strip()

                        # 画像の生成
                        image_response = client.models.generate_content(
                            model='gemini-3.1-flash-image-preview',
                            contents=english_image_prompt,
                            config={"response_modalities": ["IMAGE"]},
                        )

                        try:
                            # 画像データの抽出
                            image_bytes = image_response.candidates[0].content.parts[0].inline_data.data
                            st.session_state["persona_image"] = image_bytes
                            st.success("ペルソナ画像の生成が完了しました！")
                        except Exception as e:
                            st.error("画像データの抽出に失敗しました。")
                            st.error(f"詳細: {e}")

                except Exception as e:
                    st.error(f"生成中にエラーが発生しました: {e}")

        except Exception as e:
            st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")

    # レポート結果の表示
    if "report_text" in st.session_state:
        st.divider()
        st.subheader("📊 分析レポート")
        st.markdown(st.session_state["report_text"])

    # ペルソナ画像の表示
    if "persona_image" in st.session_state:
        st.subheader("🖼️ ターゲットペルソナ イメージ")
        st.image(st.session_state["persona_image"], caption="生成されたターゲットペルソナ画像", use_container_width=True)

if __name__ == "__main__":
    main()
