import os
from google import genai

try:
    client = genai.Client()
    models = list(client.models.list())
    for m in models:
        if 'gemma' in m.name.lower():
            print(m.name)
except Exception as e:
    print(e)
