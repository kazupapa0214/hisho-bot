import os
import hmac
import hashlib
import base64
import json
import requests
from flask import Flask, request, abort

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')

SYSTEM_PROMPT = """あなたは長山修一さんの個人秘書「クロコ」です。
長山修一さんのプロフィール：
- 箱根を中心に不動産・ホテル開発事業を運営する経営者
- 法人：ハーモニーハウス合同会社（代表）、合同会社SKY（代表）
- 介護現場10年の経験から不動産・地域再生事業へ転身
- 息子・和樹への継承が全意思決定の基準

主なプロジェクト：
1. 宮ノ下PJ：戸建リノベ（木賀10億のプロトタイプ）
2. 湯本PJ：旅館業開業（合同会社SKY）
3. 木賀1600坪PJ：本丸10億円・高級ホテル誘致
4. 宮城野MPJ：しいたけ栽培所（農福連携）

応答スタイル：
- 丁寧語不要。端的に、正確に。
- LINEのメッセージなので短く簡潔に。
- 数字は必ず正確に扱う。
"""

chat_histories = {}

def verify_signature(body: bytes, signature: str) -> bool:
    h = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), body, hashlib.sha256).digest()
    expected = base64.b64encode(h).decode('utf-8')
    return hmac.compare_digest(expected, signature)

def reply_to_line(reply_token: str, message: str):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    data = {
        'replyToken': reply_token,
        'messages': [{'type': 'text', 'text': message[:4999]}]
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=data)

def ask_groq(user_id: str, user_message: str) -> str:
    if user_id not in chat_histories:
        chat_histories[user_id] = []
    chat_histories[user_id].append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + chat_histories[user_id]
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": 1000
    }
    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    reply_text = resp.json()["choices"][0]["message"]["content"]
    chat_histories[user_id].append({"role": "assistant", "content": reply_text})
    if len(chat_histories[user_id]) > 20:
        chat_histories[user_id] = chat_histories[user_id][-20:]
    return reply_text

@app.route('/webhook', methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=False)
    if not verify_signature(body, signature):
        abort(400)
    data = json.loads(body)
    for event in data.get('events', []):
        if event.get('type') == 'message' and event['message'].get('type') == 'text':
            user_id = event['source']['userId']
            user_message = event['message']['text']
            reply_token = event['replyToken']
            try:
                response = ask_groq(user_id, user_message)
                reply_to_line(reply_token, response)
            except Exception as e:
                reply_to_line(reply_token, f'エラー：{str(e)[:100]}')
    return 'OK', 200

@app.route('/', methods=['GET'])
def health():
    return '秘書 is running', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
