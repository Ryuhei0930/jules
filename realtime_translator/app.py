import os
import json
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Mount templates
templates = Jinja2Templates(directory="realtime_translator/templates")

# Initialize Models
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    # Use Flash for speed
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    gemini_model = None

if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
else:
    openai_client = None

async def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    prompt = f"Translate the following text from {source_lang} to {target_lang}. Output ONLY the translated text, no explanations. Text: {text}"

    # Try Gemini First (Fastest/Cheapest)
    if gemini_model:
        try:
            response = await asyncio.to_thread(gemini_model.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Gemini Error: {e}")
            # Fallthrough to OpenAI

    # Try OpenAI
    if openai_client:
        try:
            response = await asyncio.to_thread(
                openai_client.chat.completions.create,
                model="gpt-4o-mini", # Fast model
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI Error: {e}")
            return "Error: Translation failed."

    return "Error: No AI model available."

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/translate")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                text = payload.get("text")
                source = payload.get("source", "ja")
                target = payload.get("target", "en")

                if text:
                    translated = await translate_text(text, source, target)
                    await websocket.send_text(json.dumps({"translated": translated}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
            except Exception as e:
                print(f"Processing Error: {e}")
                await websocket.send_text(json.dumps({"error": str(e)}))

    except WebSocketDisconnect:
        print("Client disconnected")
