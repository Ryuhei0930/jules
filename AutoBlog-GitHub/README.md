# AutoBlog AI Generator 🤖

AI関連の最新ニュースを毎日RSSで取得し、3つの異なるAIモデル（Claude、Gemini、ChatGPT）がTV番組風の討論を繰り広げるブログ記事を自動生成するシステムです。
生成された記事は、自動で `note.com` に下書き保存されます。Androidなどのスマートフォンブラウザからも簡単に実行・設定が行えるように、StreamlitベースのWeb UIを備えています。

## 🌟 主な機能

- **マルチAIによる討論形式のブログ生成**:
  - 🤖 **クロウ (Claude)**: 番組の司会進行役。ニュースの紹介、話題のフリ、最後のオチ、投げ銭（サポート）のお願い、ハッシュタグの生成を担当します。
  - 🤖 **ジェミィ (Gemini)**: 真面目なコメンテーター。ニュースの技術的な深掘りや社会への影響を専門家として解説します。
  - 🤖 **チャピオ (ChatGPT)**: コメディアン枠。ユーモアや突拍子もない未来予測で議論を盛り上げ、クスッと笑える要素を追加します。
  - 🎭 **固定ペルソナによる深い議論**: 各キャラクターの役割（冷静な司会進行のクロウ、辛口で深い洞察をするジェミィ、明るく場を和ませるチャピオ）を固定し、一貫した世界観で深く掘り下げた議論を展開します。
- **Noteへの自動投稿機能**:
  - Playwrightを用いてブラウザを自動操作し、生成したブログ記事を `note.com` に自動で下書き保存します。
- **スマートフォン対応のWeb UI**:
  - Streamlitを用いたWeb画面から、APIキーの設定、接続テスト、記事の手動生成・投稿がワンタップで可能です。
- **GitHub Actionsによる完全自動化**:
  - 指定した時間（例: 毎朝8時）に自動でニュースを取得してブログを作成するようスケジューリングできます。
- *※画像生成機能（DALL-E 3）は現在、安定性のために一時停止・削除されています。*

## 🚀 環境構築と使い方

### Streamlit Cloudでの実行（推奨・スマホ対応）

このリポジトリをStreamlit Cloudに連携するだけで、無料で自分専用のブログジェネレーターアプリを公開できます。
Playwright（ブラウザ自動化）を動かすために必要なLinuxのシステム依存関係（`packages.txt`）も自動でインストールされます。

1. **APIキーの用意**:
   以下のAPIキーとアカウント情報が必要です。
   - Gemini API Key
   - Anthropic API Key (Claude)
   - OpenAI API Key (ChatGPT)
   - note.com のログイン用メールアドレスとパスワード
2. **アプリの起動と設定**:
   - アプリを起動後、サイドバー（スマホの場合は左上のメニュー）から各APIキーとNoteのログイン情報を入力し、「設定を保存」ボタンを押してください。
   - （設定内容は `.env` に保存され、次回以降も保持されます）
3. **実行**:
   - 「今すぐブログを生成＆投稿する」ボタンを押すと、ニュース取得 → 討論生成 → noteへの下書き保存が始まります。

### ローカルでの実行

Python 3.10以上が必要です。

```bash
# 1. リポジトリのクローン
git clone https://github.com/your-username/AutoBlog-GitHub.git
cd AutoBlog-GitHub

# 2. 依存関係のインストール
pip install -r requirements.txt
playwright install chromium

# 3. Streamlitアプリの起動
streamlit run app.py
```

## 🛠️ 技術スタック

- **UI/フロントエンド**: Streamlit
- **バックエンド自動化**: Playwright (`async_playwright`)
- **AIモデル**:
  - `gemini-3-flash-preview` (Google)
  - `claude-haiku-4-5-20251001` (Anthropic)
  - `gpt-5-mini-2025-08-07` (OpenAI)
- **ニュース取得**: `feedparser`
- **インフラ/CI**: GitHub Actions, Streamlit Cloud

## 💡 注意事項

- **API利用料**: 各AIモデルのAPIを実行するため、各プラットフォームでのAPI利用料が発生する場合があります。
- **Playwrightの依存関係**: Streamlit Cloudなどで実行する場合は、必ずリポジトリのルートに `packages.txt` （libglib2.0-0, libnss3 など）が存在していることを確認してください。無いとブラウザの起動に失敗します。
- **noteのUI変更**: 自動投稿機能はnote.comのHTML構造（DOM）に依存しています。note側のUIアップデートにより自動投稿が失敗するようになった場合は、`main.py` のセレクタ指定を修正する必要があります。

## 📄 ライセンス

MIT License
