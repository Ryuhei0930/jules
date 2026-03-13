# Facebook Photo Book Maker (Prototype)

このプロジェクトは、自身のFacebookアカウントから投稿（写真とテキスト）を取得し、自動で24ページ〜48ページ（4ページ刻み）のフォトブック用PDFを生成するプロトタイプスクリプトです。

## 必須システム要件（System Requirements）

このスクリプトはHTMLからPDFを生成するために、システム全体にインストールされる `wkhtmltopdf` に依存しています。実行前に必ずOSにインストールしてください。

**Ubuntu/Debianの場合:**
```bash
sudo apt-get update
sudo apt-get install -y wkhtmltopdf
```

**macOS (Homebrew)の場合:**
```bash
brew install wkhtmltopdf
```

## セットアップ手順

1. **Pythonライブラリのインストール**
   ```bash
   pip install -r requirements.txt
   ```

2. **Facebook Graph API アクセストークンの取得**
   - [Meta for Developers](https://developers.facebook.com/) にアクセスし、新しいアプリを作成します。
   - 「Graph APIエクスプローラー」ツールを開きます。
   - あなたのアプリを選択し、「ユーザーアクセストークンを取得」をクリックします。
   - 権限として `user_posts` および `user_photos` を追加し、トークンを生成します。

3. **環境変数の設定**
   プロジェクトのルートディレクトリに `.env` という名前のファイルを作成し、取得したトークンを以下のように記述します。

   ```env
   FACEBOOK_ACCESS_TOKEN=EAACxxxxxxxxx...
   ```
   > ※ `.env` ファイルが存在しない、またはトークンが空の場合は、自動的にテスト用の「モックデータ」を使用してPDFが生成されます。

## 使い方

以下のコマンドを実行してスクリプトを起動します。

```bash
python facebook_book_maker.py
```

実行が成功すると、同じディレクトリ内に `my_facebook_book.pdf` というファイルが生成されます。

### ページ数の変更
生成するPDFのページ数を変更したい場合は、`facebook_book_maker.py` 内の以下の変数を書き換えてください。
（指定できるのは 24, 28, 32, 36, 40, 44, 48 のいずれかです）

```python
target_pages = 24  # ここを変更
```
