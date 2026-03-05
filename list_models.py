import os
from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Please set GEMINI_API_KEY environment variable")
    exit(1)

client = genai.Client(api_key=api_key)
for m in client.models.list():
    print(f"{m.name} - {m.supported_actions}")
