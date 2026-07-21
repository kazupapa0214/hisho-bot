
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHAN
NEL_SECRET', '')
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LIN
E_CHANNEL_ACCESS_TOKEN', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY
', '')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '
')

SYSTEM_PROMPT = """あなたは長山修一さんの個人秘
書「クロコ」です。
長山修一さんのプロフィール：

3. 木賀1600坪PJ：本丸10億円・高級ホテル誘致
4. 宮城野MPJ：しいたけ栽培所（農福連携）

経営哲学
1. 死から学んだ生の絶対性
2. 西陽 当てる再生
の美学）
3. 命の

応答スタ
- 丁寧語不要。端的に、正確に。
- LINEの
- 数字は必ず正確に扱う。
- 「息子 準に使う
。
"""

chat_his

    }
    requests.post('https://api.line.me/v2/bot/m
essage/rdata)

def ask_sage: str)
 -> str:
def ask_ge: str) -
> str:
    if u
        chat_histories[user_id] = []

    chat_histories[user_id].append({

        "parts": [{"text": user_message}]
    })

    url e.googleap
is.com/v1beta/models/gemini-2.0-flash:generateC
ontent?k
    chat_histories[user_id].append({"role": "us
er", "co
    messages = [{"role": "system", "content": S
YSTEM_PRid]
    url = "https://api.groq.com/openai/v1/chat/
completi
    headers = {
        OQ_API_KEY
}",
        json"
    }
    payl
        "system_instruction": {"parts": [{"text
": SYSTE
        "contents": chat_histories[user_id]
        t",
        "messages": messages,

    }
    respyload)
    resp = requests.post(url, headers=headers,
json=pay
    resp.raise_for_status()
    resu
    reply_text = result["candidates"][0]["conte
nt"]["pa

    chat
        "role": "model",
        }]
    })

    reply_text = resp.json()["choices"][0]["mes
sage"]["
    chat_histories[user_id].append({"role": "as
sistant"
    if len(chat_histories[user_id]) > 20:
        t_historie
s[user_id][-20:]

    return reply_text

@app.route('/webhook', methods=['POST'])

            user_message = event['message']['t
ext']
            reply_token = event['replyToken']

                response = ask_gemini(user_id,
 user_m
                response = ask_groq(user_id, u
ser_mes
                reply_to_line(reply_token, res
ponse)
            except Exception as e:
       token, f'
エラーが発生しました。少し待ってから再送して。
({str(e
                reply_to_line(reply_token, f'
エラー
    return 'OK', 200

@app.route('/', methods=['GET'])
