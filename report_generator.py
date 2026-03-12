import os
import json
import markdown
import pdfkit
from google import genai
import tempfile

def generate_report(ga4_data, api_key):
    """
    Geminiを使用して、GA4の生データからプロのWebマーケター視点での解析レポートを生成する。
    """
    if not api_key:
        print("❌ GEMINI_API_KEYが設定されていません。")
        return None

    try:
        print("🧠 Geminiによるレポート生成を開始します...")
        client = genai.Client(api_key=api_key)

        # JSON形式のGA4データを文字列に変換
        data_str = json.dumps(ga4_data, indent=2, ensure_ascii=False)

        prompt = f"""
        あなたは経験豊富で優秀なプロのWebデータアナリスト、およびデジタルマーケターです。
        以下のGoogle Analytics 4 (GA4) のアクセス解析データを元に、クライアント（Webサイト運営者）へ提出する**わかりやすく洞察に満ちた解析レポート**を作成してください。

        【GA4 解析データ（JSON形式）】
        ```json
        {data_str}
        ```

        【レポート作成の要件】
        1. **プロフェッショナルなトーン**: 丁寧で論理的、かつ専門用語をわかりやすく解説するトーンで記述してください。
        2. **サマリー**: まず冒頭で、全体のトラフィック傾向（セッション、ユーザー数、PV数）の概要を一目でわかるように総括してください。
        3. **詳細分析**: 日別の変動データから、トラフィックのピークや落ち込み、特筆すべき傾向（例：週末に減る、特定日に急増している等）を分析し、考えられる要因を推測してください。
        4. **課題と改善提案**: データから読み取れる現状の課題を指摘し、CVR（コンバージョン率）向上やトラフィック増加に向けた具体的なアクションプラン（Next Action）を最低3つ提案してください。
        5. **出力形式**: 美しく整った**Markdown形式**で出力してください。見出し（#や##）、箇条書き、太字を活用し、読みやすく構成してください。
        """

        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt
        )

        content = response.text
        print("✅ レポートの生成が完了しました。")
        return content

    except Exception as e:
        print(f"❌ Gemini API実行中にエラーが発生しました: {e}")
        return None

def create_pdf(markdown_text):
    """
    MarkdownテキストをHTMLに変換し、wkhtmltopdfを使用してPDFバイナリを生成する。
    """
    if not markdown_text:
        return None

    try:
        # MarkdownをHTMLに変換
        html_content = markdown.markdown(
            markdown_text,
            extensions=['tables', 'fenced_code', 'nl2br']
        )

        # HTMLをスタイリング
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: 'Helvetica Neue', Helvetica, Arial, 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{ color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                pre, code {{ background-color: #f8f9fa; border-radius: 3px; padding: 2px 4px; font-family: monospace; }}
                pre {{ padding: 10px; overflow-x: auto; }}
                ul, ol {{ margin-bottom: 20px; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        # PDFをメモリ上で生成するためのオプション設定
        options = {
            'page-size': 'A4',
            'margin-top': '20mm',
            'margin-right': '20mm',
            'margin-bottom': '20mm',
            'margin-left': '20mm',
            'encoding': "UTF-8",
            'no-outline': None
        }

        # PDFを一時ファイルとして作成
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf:
            pdfkit.from_string(styled_html, tmp_pdf.name, options=options)
            tmp_pdf_path = tmp_pdf.name

        # PDFをバイナリとして読み込む
        with open(tmp_pdf_path, 'rb') as f:
            pdf_bytes = f.read()

        # 一時ファイルを削除
        os.remove(tmp_pdf_path)

        return pdf_bytes

    except Exception as e:
        print(f"❌ PDF変換中にエラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    # Test script
    sample_data = {
      "property_id": "99999",
      "period": "Last 7 days to today",
      "totals": {"sessions": 1500, "active_users": 1200, "page_views": 3200},
      "daily_data": [
        {"date": "20231001", "sessions": 200, "active_users": 150, "page_views": 400},
        {"date": "20231002", "sessions": 250, "active_users": 200, "page_views": 500}
      ]
    }
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        report = generate_report(sample_data, api_key)
        print("Generated Report (Markdown):")
        print(report)
        print("Generating PDF...")
        pdf = create_pdf(report)
        if pdf:
            print("PDF generation successful (bytes length: {})".format(len(pdf)))
        else:
            print("PDF generation failed.")
    else:
        print("Skipping Gemini test: GEMINI_API_KEY not found in environment.")
