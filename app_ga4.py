import streamlit as st
import os
import tempfile
from dotenv import load_dotenv
from ga4_fetcher import fetch_ga4_data
from report_generator import generate_report, create_pdf

# Load environment variables
load_dotenv()

st.set_page_config(page_title="GA4 Web解析レポートAI", page_icon="📊", layout="wide")

st.title("🤖 GA4 Web解析レポート エージェントAI")
st.write("GA4のデータを取得し、AI（Gemini）がプロのWebマーケターとして分析レポートを自動生成します。")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ 設定 / Settings")

    with st.form("config_form"):
        property_id = st.text_input(
            "GA4 プロパティID",
            value=os.getenv("GA4_PROPERTY_ID", ""),
            placeholder="例: 123456789",
            help="Google Analytics 4 のプロパティIDを入力してください。"
        )

        days_ago = st.slider(
            "解析期間（過去何日間）",
            min_value=1, max_value=90, value=7,
            help="データを取得する期間を指定します。"
        )

        credentials_json = st.text_area(
            "Google Service Account JSON",
            placeholder='{"type": "service_account", ...}',
            help="GA4 Data APIにアクセスするためのサービスアカウントのJSONキー内容を貼り付けてください。空の場合は環境変数 `GOOGLE_APPLICATION_CREDENTIALS` を使用します。"
        )

        gemini_api_key = st.text_input(
            "Gemini API Key",
            value=os.getenv("GEMINI_API_KEY", ""),
            type="password",
            help="レポート生成に使用するGeminiのAPIキーを入力してください。"
        )

        submit_button = st.form_submit_button("設定を保存 & 実行準備")

# Main execution area
if submit_button:
    if not property_id:
        st.error("GA4 プロパティIDを入力してください。")
        st.stop()
    if not gemini_api_key:
        st.error("Gemini API Keyを入力してください。")
        st.stop()

    st.session_state['ready_to_run'] = True

if st.session_state.get('ready_to_run', False):
    if st.button("🚀 レポート生成を開始する", type="primary", use_container_width=True):
        with st.spinner("GA4からデータを取得中..."):
            # Handle Service Account JSON
            credentials_path = None
            if credentials_json:
                # Create a temporary file for the JSON credentials
                fd, credentials_path = tempfile.mkstemp(suffix=".json")
                with os.fdopen(fd, 'w') as f:
                    f.write(credentials_json)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

            try:
                ga4_data = fetch_ga4_data(property_id, days_ago)

                if not ga4_data:
                    st.error("GA4データの取得に失敗しました。プロパティIDやJSONキー、権限を確認してください。")
                    st.stop()

                st.success("GA4データの取得に成功しました！")

                with st.expander("取得したGA4生データ（デバッグ用）"):
                    st.json(ga4_data)

            except Exception as e:
                st.error(f"GA4データ取得中にエラーが発生しました: {e}")
                st.stop()
            finally:
                # Cleanup temp file if created
                if credentials_path and os.path.exists(credentials_path):
                    os.remove(credentials_path)

        with st.spinner("AI(Gemini)がレポートを執筆中..."):
            try:
                report_markdown = generate_report(ga4_data, gemini_api_key)

                if not report_markdown:
                    st.error("レポートの生成に失敗しました。")
                    st.stop()

                st.success("レポート生成完了！")
                st.session_state['report_markdown'] = report_markdown

            except Exception as e:
                st.error(f"レポート生成中にエラーが発生しました: {e}")
                st.stop()

# Display report and download button
if 'report_markdown' in st.session_state:
    st.markdown("---")
    st.subheader("📄 生成された解析レポート")

    report_md = st.session_state['report_markdown']
    st.markdown(report_md)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.download_button(
            label="⬇️ Markdownファイルとしてダウンロード",
            data=report_md,
            file_name=f"ga4_report_{property_id}.md",
            mime="text/markdown",
            use_container_width=True
        )

    with col2:
        with st.spinner("PDFファイルを生成中..."):
            pdf_bytes = create_pdf(report_md)
            if pdf_bytes:
                st.download_button(
                    label="⬇️ PDFファイルとしてダウンロード",
                    data=pdf_bytes,
                    file_name=f"ga4_report_{property_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.error("PDFの生成に失敗しました。")
