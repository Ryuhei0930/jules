# リアルタイムAI翻訳機 (日 <-> 英)

モバイル利用を想定した、超高速・軽量なリアルタイム翻訳ウェブアプリです。
Web Speech APIによる遅延ゼロの音声認識・音声合成と、高速な生成AIモデル（Gemini 1.5 Flash または GPT-4o-mini）を組み合わせることで、高精度かつ即時の翻訳を実現しています。

## 特徴

- **世界最速級のアーキテクチャ**: 音声認識（STT）と音声合成（TTS）をブラウザ側でローカル処理し、ネットワーク遅延を最小限に抑えています。サーバーへ送信されるのは翻訳テキストのみです。
- **モバイルファースト**: スマートフォンのブラウザですぐに起動できるよう、シンプルなタッチインターフェースを採用しています。
- **最新AI搭載**: GoogleのGemini 1.5 Flash（推奨・最速）またはOpenAIのGPT-4o-mini（バックアップ）を使用し、文脈を理解した自然な翻訳を提供します。

## 前提条件

- Python 3.10以上
- Google Gemini (`GEMINI_API_KEY`) または OpenAI (`OPENAI_API_KEY`) のAPIキー。

## インストール手順

1.  リポジトリのルートディレクトリに移動します。

2.  依存関係をインストールします:
    ```bash
    pip install -r realtime_translator/requirements.txt
    ```

## 使い方

1.  プロジェクトルートにある `.env` ファイルにAPIキーを設定してください:
    ```
    GEMINI_API_KEY=your_gemini_key
    OPENAI_API_KEY=your_openai_key
    ```

2.  サーバーを起動します (リポジトリのルートから実行):
    ```bash
    uvicorn realtime_translator.app:app --reload --host 0.0.0.0 --port 8000
    ```

3.  アプリにアクセスします:
    -   **PC (ローカル)**: ブラウザで `http://localhost:8000` を開きます。
    -   **スマートフォン**: PCとスマホを同じWi-Fiに接続し、PCのIPアドレス（例: `192.168.1.5`）を確認して、スマホのブラウザで `http://192.168.1.5:8000` を開きます。

## HTTPSに関する注意 (スマホ利用時)
iPhone (iOS) やAndroidの一部ブラウザでは、マイクを使用するためにサイトが **HTTPS** で配信されている必要があります。
ローカル環境でテストする場合は、`ngrok` などのツールを使用することをお勧めします。

1.  `ngrok` をインストールして実行:
    ```bash
    ngrok http 8000
    ```
2.  表示されたHTTPSのURL（例: `https://xxxx-xxxx.ngrok-free.app`）をスマホで開いてください。
