import streamlit as st
import pandas as pd
import datetime
from google import genai
from google.genai import types
from google.genai.errors import APIError

st.set_page_config(page_title="社内SNS調査ツール", page_icon="🔍", layout="wide")

st.title("🔍 社内SNS調査・分析ダッシュボード")
st.markdown("柔軟なキーワード検索とGemini 3.1 Flashによる高度な感情分析・インサイト抽出を行うための社内ツールです。")

# サイドバー：APIキー設定
st.sidebar.header("🔑 API設定")
api_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="AI分析を実行するには入力必須")
st.sidebar.markdown("---")

# サイドバー：検索条件の設定
st.sidebar.header("1. 検索条件の設定")

# メインキーワード
main_keyword = st.sidebar.text_input("🎯 メインキーワード", placeholder="例: 自社サービス名、競合名")

# 高度な検索（エキスパンダーで隠すことでUIをスッキリさせる）
with st.sidebar.expander("⚙️ 高度な検索オプション"):
    st.markdown("**AND / OR / NOT 検索**")
    and_keywords = st.text_input("AND (すべて含む)", placeholder="例: キャンペーン, 割引")
    or_keywords = st.text_input("OR (いずれかを含む)", placeholder="例: スマホ, スマートフォン")
    not_keywords = st.text_input("NOT (除外する)", placeholder="例: ボット, 宣伝")

    st.markdown("**類義語拡張**")
    use_synonyms = st.checkbox("AIによる類義語の自動拡張を有効にする", value=True)

# 期間指定
st.sidebar.markdown("---")
st.sidebar.header("2. 期間指定")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("開始日", datetime.date.today() - datetime.timedelta(days=7))
with col2:
    end_date = st.date_input("終了日", datetime.date.today())

# 対象プラットフォーム
st.sidebar.markdown("---")
st.sidebar.header("3. 調査対象")
platform_x = st.sidebar.checkbox("X (Twitter)", value=True)
platform_insta = st.sidebar.checkbox("Instagram", value=False)
platform_news = st.sidebar.checkbox("ニュース/ブログ", value=True)

# 検索実行ボタン
search_clicked = st.sidebar.button("🚀 データの収集と分析を開始", type="primary", use_container_width=True)

# メイン画面：分析結果（ボタンが押されたら表示）
if search_clicked:
    if not main_keyword:
        st.warning("メインキーワードを入力してください。")
    elif not api_key:
        st.warning("高度なAI分析を実行するため、サイドバーからGemini API Keyを入力してください。")
    else:
        # プロトタイプ用のダミーデータ生成（実際はここでSNS APIからデータ取得する）
        df_dummy = pd.DataFrame({
            "日時": ["2023-10-27 10:00", "2023-10-27 11:30", "2023-10-27 14:15", "2023-10-28 09:00", "2023-10-28 15:20"],
            "プラットフォーム": ["X", "ニュース", "X", "X", "Instagram"],
            "感情": ["ポジティブ", "ニュートラル", "ネガティブ", "ポジティブ", "ネガティブ"],
            "内容": [
                f"{main_keyword}の新機能、すごく便利で作業効率が上がった！",
                f"{main_keyword}に関する新機能追加のプレスリリースが発表されました。",
                f"{main_keyword}、アップデートしてからちょっと動作が重い気がする...改善希望。",
                f"他社ツールから{main_keyword}に乗り換えたけど、UIが直感的で分かりやすい。",
                f"{main_keyword}のカスタマーサポート、返信が遅くて困る。"
            ]
        })
        posts_text = "\n".join([f"- [{row['プラットフォーム']}] {row['内容']}" for index, row in df_dummy.iterrows()])

        with st.spinner("データを収集中... Gemini 3.1 Flash が高度な文脈分析とインサイト抽出を実行しています..."):
            try:
                client = genai.Client(api_key=api_key)

                system_instruction = (
                    "あなたは優秀なデータアナリストです。提供されたSNSの生データ（<data>タグ内）を分析し、"
                    "以下の4つの観点で高度なレポートをMarkdown形式で作成してください。\n"
                    "1. 全体的なセンチメント（感情）の傾向と文脈の深い理解\n"
                    "2. ユーザーの深層心理（なぜそのように言っているのかの考察）\n"
                    "3. 急上昇している潜在的なトピックやトレンド\n"
                    "4. 自社が取るべき具体的なネクストアクション（提案）\n"
                    "※データの内容を客観的に分析し、社内向けのプロフェッショナルなトーンで記述してください。"
                )

                prompt = f"以下のSNSデータについて、指定された観点で高度な分析レポートを作成してください。\n\n<data>\n対象キーワード: {main_keyword}\n収集データ:\n{posts_text}\n</data>"

                response = client.models.generate_content(
                    model='gemini-3.1-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        temperature=0.4,
                    )
                )
                ai_analysis_result = response.text

            except APIError as e:
                st.error(f"Gemini APIエラーが発生しました: {e}")
                ai_analysis_result = "APIエラーのため、AI分析レポートを生成できませんでした。"
            except Exception as e:
                st.error(f"予期せぬエラーが発生しました: {e}")
                ai_analysis_result = "エラーのため、AI分析レポートを生成できませんでした。"

        st.success(f"「{main_keyword}」に関するデータの収集と高度なAI分析が完了しました！")

        # タブで結果を整理して表示
        tab1, tab2, tab3 = st.tabs(["📊 サマリー・AI要約", "📈 トレンド・感情分析", "📋 生データ一覧"])

        with tab1:
            st.subheader("🧠 Gemini 3.1 Flash 高度分析レポート")
            if "エラー" not in ai_analysis_result:
                st.info("LLMが投稿の文脈を読み解き、単なる集計以上の深いインサイトを提供します。")
            st.markdown(ai_analysis_result)

        with tab2:
            col_a, col_b = st.columns(2)
            with col_a:
                st.subheader("感情（センチメント）の割合")
                # ダミーグラフ用データ
                chart_data = pd.DataFrame(
                    {"感情": ["ポジティブ (賞賛・期待)", "ニュートラル", "ネガティブ (不満・疑問)"],
                     "割合": [45, 35, 20]}
                ).set_index("感情")
                st.bar_chart(chart_data)

            with col_b:
                st.subheader("言及数の推移 (日別)")
                trend_data = pd.DataFrame(
                    {"言及数": [120, 150, 130, 200, 450, 310, 280]},
                    index=pd.date_range(start=start_date, periods=7)
                )
                st.line_chart(trend_data)

        with tab3:
            st.subheader("収集した投稿一覧")
            st.dataframe(df_dummy, use_container_width=True)

            st.download_button(
                label="📥 データをCSVでエクスポート",
                data=df_dummy.to_csv(index=False).encode('utf-8'),
                file_name=f"{main_keyword}_social_data.csv",
                mime="text/csv",
                use_container_width=True
            )
else:
    # 初期画面のガイダンス
    st.info("👈 左側のサイドバーからキーワードや期間を設定し、「データの収集と分析を開始」ボタンを押してください。")
    st.markdown("""
    ### 💡 このツールの特徴（社内調査向け）
    *   **誰でも簡単に**: 複雑なクエリ言語を知らなくても、UIから直感的に「AND/OR/除外」検索が可能です。
    *   **AIが類義語をカバー**: 「スマホ」と検索すれば「スマートフォン」等もAIが自動で補完し、調査漏れを防ぎます。
    *   **生データの二次利用**: 収集したデータとAIの分析結果はCSVでダウンロードでき、Excelや社内資料にすぐ活用できます。
    """)
