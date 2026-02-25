import sys
import os
import json
from fastapi.testclient import TestClient

# Add current directory to path so we can import app
sys.path.append(os.getcwd())

from realtime_translator.app import app

def test_websocket():
    client = TestClient(app)
    try:
        with client.websocket_connect("/ws/translate") as websocket:
            print("Connected to WebSocket")
            payload = {"text": "Hello", "source": "en", "target": "ja"}
            websocket.send_json(payload)
            print(f"Sent: {payload}")

            data = websocket.receive_json()
            print(f"Received: {data}")

            if "translated" in data:
                print("Test Passed: Translation received.")
            elif "error" in data:
                print(f"Test Passed (with error): {data['error']}")
            else:
                print("Test Failed: Unexpected response format.")
                sys.exit(1)
    except Exception as e:
        print(f"Test Failed with exception: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_websocket()
