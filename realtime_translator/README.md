# Real-time AI Translator (JP <-> EN)

A lightweight, ultra-fast real-time translation web app designed for mobile usage.
It leverages the Web Speech API for zero-latency speech recognition and synthesis, combined with fast Generative AI models (Gemini 1.5 Flash or GPT-4o-mini) for accurate translation.

## Features

- **World's Fastest Architecture**: Uses local browser-based Speech-to-Text (STT) and Text-to-Speech (TTS) to minimize network latency. Only the text translation goes to the server.
- **Mobile First**: Designed to launch instantly on mobile browsers with a simple touch interface.
- **AI-Powered**: Uses Google's Gemini 1.5 Flash (primary) or OpenAI's GPT-4o-mini (fallback) for context-aware translations.

## Prerequisites

- Python 3.10+
- An API Key for Google Gemini (`GEMINI_API_KEY`) or OpenAI (`OPENAI_API_KEY`).

## Installation

1.  Navigate to the repository root.

2.  Install dependencies:
    ```bash
    pip install -r realtime_translator/requirements.txt
    ```

## Usage

1.  Ensure your `.env` file in the project root contains your API keys:
    ```
    GEMINI_API_KEY=your_gemini_key
    OPENAI_API_KEY=your_openai_key
    ```

2.  Start the server from the repository root:
    ```bash
    uvicorn realtime_translator.app:app --reload --host 0.0.0.0 --port 8000
    ```

3.  Access the app:
    -   **Local**: Open `http://localhost:8000`
    -   **Mobile**: Connect your phone to the same Wi-Fi as your computer, find your computer's IP address (e.g., `192.168.1.5`), and open `http://192.168.1.5:8000` on your phone.

## Note on HTTPS
For the microphone to work on mobile devices (especially iOS/Android), the site often needs to be served over HTTPS.
-   **Local Development**: You can use tools like `ngrok` or `mkcert`.
    ```bash
    ngrok http 8000
    ```
    Then open the ngrok HTTPS URL on your phone.
