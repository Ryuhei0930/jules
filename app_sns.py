import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="社内SNS調査ツール", page_icon="🔍", layout="wide")

st.title("🔍 社内SNS調査・分析ダッシュボード (プロトタイプ)")
st.markdown("柔軟なキーワード検索とAIによる感情分析・要約を行うための社内ツールです。")

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
    else:
        with st.spinner("データを収集中... AIが感情分析と要約を実行しています..."):
            # ※ここはプロトタイプ用のダミーデータ表示です
            import time
            time.sleep(2)

        st.success(f"「{main_keyword}」に関する分析が完了しました！")

        # タブで結果を整理して表示
        tab1, tab2, tab3 = st.tabs(["📊 サマリー・AI要約", "📈 トレンド・感情分析", "📋 生データ一覧"])

        with tab1:
            st.subheader("💡 AIによるインサイト要約")
            st.info(
                f"**【全体傾向】**\n"
                f"指定期間内において「{main_keyword}」に関する言及は増加傾向にあります。特に昨日から急増しています。\n\n"
                f"**【ポジティブな声】**\n"
                f"・「使いやすくなった」「デザインが良い」といったUI/UXに関する評価が高いです。\n\n"
                f"**【改善要望・ネガティブな声】**\n"
                f"・一部のユーザーから「アプリの起動が遅い」という不満が挙げられています。至急の確認を推奨します。"
            )

            st.subheader("🔥 急上昇関連ワード")
            st.markdown("- #アップデート最高\n- 起動遅い\n- 代替アプリ")

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
            # ダミーデータフレーム
            df_dummy = pd.DataFrame({
                "日時": ["2023-10-27 10:00", "2023-10-27 11:30", "2023-10-27 14:15"],
                "プラットフォーム": ["X", "ニュース", "X"],
                "感情": ["ポジティブ", "ニュートラル", "ネガティブ"],
                "内容": [f"{main_keyword}の新機能、すごく便利！", f"{main_keyword}に関するプレスリリースが発表されました。", f"{main_keyword}、ちょっと動作が重い気がする..."]
            })
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
