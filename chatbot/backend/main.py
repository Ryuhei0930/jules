import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv, find_dotenv

# Try to find .env file dynamically (starts from current working directory and goes up)
dotenv_path = find_dotenv()

# Fallback to the same directory as main.py if find_dotenv() didn't find one
if not dotenv_path:
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

load_dotenv(dotenv_path=dotenv_path)

app = FastAPI()

# Allow CORS for the frontend widget
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with the specific domain(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Verification on Startup
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    # Just checking if the variable is loaded, do not log the key itself
    print("✅ GEMINI_API_KEY: 読み込み成功")
else:
    print("❌ GEMINI_API_KEY: 未設定 (API呼び出し時にエラーになります)")

# Load Knowledge Base (CSV)
KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "knowledge.csv")
knowledge_text = ""

try:
    if os.path.exists(KNOWLEDGE_FILE):
        print(f"📄 CSV読み込み先: {KNOWLEDGE_FILE}")
        df = pd.read_csv(KNOWLEDGE_FILE)
        # Assuming the CSV has at least two columns, like "Question" and "Answer" or similar chunks
        # We will concatenate all rows into a single text block for the prompt context.
        chunks = []
        for index, row in df.iterrows():
            row_text = " | ".join([f"{col}: {str(val)}" for col, val in row.items() if pd.notna(val)])
            chunks.append(row_text)
        knowledge_text = "\n".join(chunks)
        print(f"✅ CSVデータ: {len(chunks)} 個のチャンクを読み込みました")
    else:
        print(f"⚠️ 警告: CSVファイルが見つかりません。ナレッジなしで起動します。 (探索パス: {KNOWLEDGE_FILE})")
except Exception as e:
    print(f"❌ CSV読み込みエラー ({KNOWLEDGE_FILE}): {e}")

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY is not set.")

    try:
        client = genai.Client(api_key=api_key)

        # Construct the prompt with the knowledge base
        system_instruction = (
            "あなたはユーザーの質問に答える親切なアシスタントです。"
            "以下の【提供された知識】に基づいて回答してください。"
            "提供された知識に答えがない場合は、「申し訳ありませんが、その情報はお答えできません。」と答えてください。\n\n"
            "【提供された知識】\n"
            f"{knowledge_text}\n"
        )

        prompt = f"ユーザーの質問: {request.message}"

        response = client.models.generate_content(
            model='gemini-3.1-flash', # Requested model
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3, # Keep it somewhat deterministic for factual Q&A
            )
        )

        return ChatResponse(response=response.text)

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        raise HTTPException(status_code=500, detail="Error generating response.")

@app.get("/")
async def root():
    return {"message": "Chatbot API is running."}
