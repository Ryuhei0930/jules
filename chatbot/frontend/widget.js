(function() {
    // === 設定 ===
    // FastAPIバックエンドのURLを指定してください (ローカル環境用)
    const API_URL = 'http://127.0.0.1:8000/chat';

    // === スタイルシートの動的追加 ===
    const style = document.createElement('style');
    style.innerHTML = `
        #my-chatbot-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 500px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            font-family: sans-serif;
            z-index: 10000;
            display: none; /* 初期状態は非表示 */
        }
        #my-chatbot-header {
            background-color: #007bff;
            color: #fff;
            padding: 15px;
            font-weight: bold;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #my-chatbot-close {
            cursor: pointer;
            font-size: 20px;
            line-height: 1;
        }
        #my-chatbot-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            background-color: #f9f9f9;
            display: flex;
            flex-direction: column;
            gap: 10px;
        }
        .my-chatbot-msg {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 15px;
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }
        .my-chatbot-msg.user {
            align-self: flex-end;
            background-color: #e0f7fa;
            color: #006064;
            border-bottom-right-radius: 2px;
        }
        .my-chatbot-msg.bot {
            align-self: flex-start;
            background-color: #fff;
            color: #333;
            border: 1px solid #ddd;
            border-bottom-left-radius: 2px;
        }
        #my-chatbot-input-area {
            display: flex;
            padding: 10px;
            border-top: 1px solid #ddd;
            background-color: #fff;
        }
        #my-chatbot-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            outline: none;
        }
        #my-chatbot-send {
            margin-left: 10px;
            padding: 10px 15px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: bold;
        }
        #my-chatbot-send:hover {
            background-color: #0056b3;
        }
        #my-chatbot-launcher {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #007bff;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            color: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            z-index: 9999;
        }
        #my-chatbot-launcher:hover {
            background-color: #0056b3;
        }
    `;
    document.head.appendChild(style);

    // === HTML要素の構築 ===
    const launcher = document.createElement('div');
    launcher.id = 'my-chatbot-launcher';
    launcher.innerHTML = '💬'; // チャットアイコン
    document.body.appendChild(launcher);

    const container = document.createElement('div');
    container.id = 'my-chatbot-container';
    container.innerHTML = `
        <div id="my-chatbot-header">
            <span>カスタマーサポート</span>
            <span id="my-chatbot-close">×</span>
        </div>
        <div id="my-chatbot-messages"></div>
        <div id="my-chatbot-input-area">
            <input type="text" id="my-chatbot-input" placeholder="質問を入力..." />
            <button id="my-chatbot-send">送信</button>
        </div>
    `;
    document.body.appendChild(container);

    // === 要素の取得 ===
    const messagesDiv = document.getElementById('my-chatbot-messages');
    const inputField = document.getElementById('my-chatbot-input');
    const sendBtn = document.getElementById('my-chatbot-send');
    const closeBtn = document.getElementById('my-chatbot-close');

    // === UIの制御 ===
    launcher.addEventListener('click', () => {
        container.style.display = 'flex';
        launcher.style.display = 'none';
        if (messagesDiv.children.length === 0) {
            addMessage('bot', 'こんにちは！何かご質問はありますか？');
        }
    });

    closeBtn.addEventListener('click', () => {
        container.style.display = 'none';
        launcher.style.display = 'flex';
    });

    // === メッセージ追加関数 ===
    function addMessage(sender, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `my-chatbot-msg ${sender}`;
        msgDiv.innerText = text;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    // === バックエンドとの通信 ===
    async function sendMessage() {
        const text = inputField.value.trim();
        if (!text) return;

        addMessage('user', text);
        inputField.value = '';
        inputField.disabled = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            addMessage('bot', data.response);

        } catch (error) {
            console.error('Error:', error);
            addMessage('bot', 'エラーが発生しました。しばらく経ってからもう一度お試しください。');
        } finally {
            inputField.disabled = false;
            sendBtn.disabled = false;
            inputField.focus();
        }
    }

    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

})();
