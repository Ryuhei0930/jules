# AutoBlog-GitHub (AI News Blog Automator)

このプロジェクトは、毎日朝8時（日本時間）にAI関連ニュースをRSSで収集し、Gemini, Claude, ChatGPT, DALL-E 3を使用して「AI討論形式」のブログ記事を作成し、note.comに自動的に下書き保存するPythonスクリプトです。GitHub Actions上で動作します。

## 主な機能
*   **RSS取得**: 最新のAIニュースを取得。
*   **AI討論生成**:
    *   **Gemini (gemini-3-flash-preview)**: ニュース要約と解説。
    *   **Claude (claude-haiku-4-5-20251001)**: 討論台本の作成（収益化を意識した司会進行）。
    *   **ChatGPT (gpt-5-mini-2025-08-07)**: 画像プロンプト生成。
    *   **DALL-E 3**: 記事のアイキャッチ画像を生成。
*   **自動投稿**: Playwrightを使用してnote.comにログインし、記事の本文と画像を入力して下書き保存します。
*   **スケジュール実行**: 毎日朝8時に自動実行。
*   **手動実行**: スマホのGitHubアプリからいつでも実行可能。

## セットアップ手順

1.  **リポジトリのフォーク**: このリポジトリを自分のGitHubアカウントにフォークします。

2.  **APIキーの取得**: 以下のサービスのAPIキーが必要です。
    *   Google Gemini API Key
    *   Anthropic API Key (Claude)
    *   OpenAI API Key (ChatGPT/DALL-E)

3.  **GitHub Secretsの設定**:
    *   リポジトリの `Settings` > `Secrets and variables` > `Actions` に移動します。
    *   以下の名前でシークレットを追加してください。
        *   `RSS_URL`: RSSフィードのURL（例: `https://feeds.feedburner.com/TechCrunch/`）
        *   `GEMINI_API_KEY`: 取得したGemini APIキー
        *   `ANTHROPIC_API_KEY`: 取得したAnthropic APIキー
        *   `OPENAI_API_KEY`: 取得したOpenAI APIキー
        *   `NOTE_EMAIL`: note.comのログインメールアドレス
        *   `NOTE_PASSWORD`: note.comのログインパスワード

4.  **スマホからの実行方法**:
    *   GitHubモバイルアプリをインストールしてログインします。
    *   このリポジトリを開き、`Actions` タブに移動します。
    *   `Daily AI Blog Automation` ワークフローを選択します。
    *   右上の `Run workflow` ボタンをタップすると、スクリプトが手動実行されます。

## 注意事項
*   **Noteの仕様変更**: note.comのデザインやログインフローが変更されると、自動投稿機能が動かなくなる可能性があります。その場合は `main.py` の修正が必要です。
*   **APIコスト**: AI APIの使用料金が発生します。各サービスの利用状況を確認してください。
*   **画像アップロード**: スクリプトは画像のアップロードを試みますが、UIの変更により失敗する場合があります。その場合はテキストのみ下書き保存されます。
*   **2段階認証**: note.comで2段階認証を有効にしている場合、自動ログインは失敗します。一時的に無効にするか、Cookieを使用した高度な実装への変更が必要です。

## ライセンス
MIT License
