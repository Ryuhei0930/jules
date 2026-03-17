# Webサイト埋め込み用 カスタムAIチャットボット

このプロジェクトは、自社のWebサイトに1行のスクリプトを記述するだけで埋め込むことができる、AIチャットボットのカスタム実装（Python FastAPI + Vanilla JS）です。
社外のプラットフォーム（Dify等）にデータを公開したくない場合に、自社サーバーで完結して動作させることができます。

## 構成
* **Backend (`backend/`):** FastAPIを使用したPythonサーバーです。Gemini 3.1 Flashを利用し、CSVから読み込んだ知識（チャンク）をもとに回答を生成します。
* **Frontend (`frontend/`):** 任意のWebサイトに埋め込めるチャットUIを提供するJavaScriptウィジェットです。

---

## バックエンドのセットアップと実行

1. **環境変数の設定**
   プロジェクトのルートディレクトリ（または`backend/`内）に `.env` ファイルを作成し、GeminiのAPIキーを設定します。
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```

2. **依存関係のインストール**
   ルートディレクトリの `requirements.txt` を使用して必要なパッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```

3. **知識ベース（CSV）の準備**
   `backend/knowledge.csv` にボットに学習させたいQ&Aや情報を記載します。
   1行目がヘッダー（例: `Q,A` など）、2行目以降がデータになります。このCSVの内容がGeminiのプロンプトにコンテキストとして渡されます。

4. **サーバーの起動**
   ルートディレクトリから以下のコマンドを実行してFastAPIサーバーを起動します。
   ```bash
   uvicorn chatbot.backend.main:app --reload
   ```
   *デフォルトでは `http://127.0.0.1:8000` でサーバーが立ち上がります。*

---

## フロントエンドの埋め込みとテスト

1. **ウィジェットのテスト**
   ブラウザで `frontend/index.html` を直接開くことで、チャットボットのUIと動作をテストできます。（※バックエンドサーバーが起動している必要があります）

2. **自社サイトへの埋め込み方法**
   自社のWebサイトのHTMLの `<body>` タグ内の最下部などに、以下の1行を追加するだけでチャットボットが表示されます。
   ```html
   <script src="https://your-domain.com/path/to/widget.js"></script>
   ```

3. **本番環境に向けた設定変更**
   * **`frontend/widget.js`:**
     2行目付近にある `const API_URL = 'http://127.0.0.1:8000/chat';` を、実際にデプロイしたバックエンドサーバーのURLに変更してください。
   * **`backend/main.py`:**
     CORSの設定部分（`allow_origins=["*"]`）を、セキュリティ向上のため、ウィジェットを埋め込む自社サイトのドメインのみ許可するように変更してください。
