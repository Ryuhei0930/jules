import socket
import uvicorn
import sys
import os

def get_local_ip():
    """Detects the local IP address connected to the network."""
    try:
        # Connect to a public DNS server (Google's) to determine the outgoing interface IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"

def main():
    port = 8000
    host = "0.0.0.0"

    local_ip = get_local_ip()

    print("\n" + "="*50)
    print(" 🚀 Real-time AI Translator Server Started!")
    print("="*50)
    print(f"\n💻 Access on this computer: http://localhost:{port}")
    if local_ip != "127.0.0.1":
        print(f"📱 Access from Smartphone (Wi-Fi): http://{local_ip}:{port}")
    else:
        print("⚠️ Could not detect local network IP. Use `ipconfig` or `ifconfig` to find it manually.")

    print("\n⚠️ IMPORTANT NOTE for Mobile Users:")
    print("   iOS (iPhone) and many Android browsers require HTTPS for microphone access.")
    print("   If the microphone doesn't work, use a secure tunnel like ngrok:")
    print(f"   Run: `ngrok http {port}` and use the https:// URL provided.")
    print("\n" + "="*50 + "\n")

    # Run Uvicorn server programmatically
    # "realtime_translator.app:app" must be importable, so ensure root is in path
    sys.path.append(os.getcwd())

    try:
        uvicorn.run("realtime_translator.app:app", host=host, port=port, reload=True)
    except KeyboardInterrupt:
        print("\nStopping server...")

if __name__ == "__main__":
    main()
