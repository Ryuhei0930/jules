# GA4 Web解析レポート エージェントAI (AutoBlog-GitHub / Streamlit)

Google Analytics Data API (GA4) を使用して指定期間のアクセスデータを取得し、Gemini APIを用いてプロのWebマーケター視点での解析レポート（Markdown/PDF）を自動生成するStreamlit Webアプリケーションです。

## 必須要件 (Requirements)

- Python 3.9+
- `wkhtmltopdf` (PDF生成機能に必須)

### wkhtmltopdf のインストール方法

PDF生成に `pdfkit` を使用しているため、OSに `wkhtmltopdf` がインストールされている必要があります。

- **Ubuntu/Debian**: `sudo apt-get install wkhtmltopdf`
- **macOS (Homebrew)**: `brew install wkhtmltopdf`
- **Windows**: [公式サイト](https://wkhtmltopdf.org/downloads.html)からインストーラーをダウンロードし、環境変数(PATH)を通してください。

## セットアップ手順

1. パッケージのインストール:
   ```bash
   pip install -r requirements.txt
   ```
2. （任意）`.env` ファイルを作成し、環境変数を設定します:
   ```env
   GA4_PROPERTY_ID=あなたのGA4プロパティID
   GEMINI_API_KEY=あなたのGemini APIキー
   # ローカル実行の場合は、以下のパスを指定することも可能です
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service_account.json
   ```

## 起動方法

```bash
streamlit run app_ga4.py
```
ブラウザが開き、UI画面から設定項目を入力してレポートを生成できます。

## 注意事項

- UI上で「Google Service Account JSON」を貼り付けた場合、一時的にファイルを作成して `GOOGLE_APPLICATION_CREDENTIALS` 環境変数を上書きします。このアプリはシングルユーザー/ローカル環境での利用を想定しており、複数ユーザーが同時にアクセスする本番環境ではセッションの競合が発生する可能性があります。
