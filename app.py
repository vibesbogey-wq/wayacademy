import os
import requests
from flask import Flask, request

from dotenv import load_dotenv
from openai import OpenAI

# ---------------- ENV АЧААЛЛАХ ---------------- #

# .env файлаас тохиргоо уншина
# (.env дотороо:
#   PAGE_ACCESS_TOKEN=...
#   VERIFY_TOKEN=...
#   OPENAI_API_KEY=...
#  гэж хадгалсан байх ёстой)
load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not PAGE_ACCESS_TOKEN:
    raise RuntimeError("PAGE_ACCESS_TOKEN environment variable байхгүй байна!")
if not VERIFY_TOKEN:
    raise RuntimeError("VERIFY_TOKEN environment variable байхгүй байна!")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY environment variable байхгүй байна!")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# ---------------- FAQ өгөгдөл ---------------- #

FAQ_LIST = [
    {
        "q_keywords": ["цаг", "нээлттэй", "хаадаг", "working hours", "open"],
        "answer": "🕒 Манай ажиллах цаг: Даваа–Ням 10:00–20:00. Амралтын өдөргүй."
    },
    {
        "q_keywords": ["хаана", "байрладаг", "location", "address", "хаяг"],
        "answer": "📍 Хаяг: Улаанбаатар, ... (энд өөрийн бодит хаягаа бичээрэй)."
    },
    {
        "q_keywords": ["үнэ", "үнийн", "price", "хямдрал", "sale"],
        "answer": "💰 Үнэ загвараас хамаарна. Яг сонирхож буй барааны зургаа эсвэл линкээ явуулбал дэлгэрэнгүй үнэ хэлж өгнө."
    },
    {
        "q_keywords": ["хүргэлт", "delivery"],
        "answer": "🚚 УБ дотор хүргэлттэй. Төлбөрөө бүрэн шилжүүлсний дараа 24 цагийн дотор хүргэнэ."
    },
    {
        "q_keywords": ["утас", "холбогдох", "contact"],
        "answer": "☎️ Холбогдох утас: 9ХХХ-ХХХХ. Messenger-ээр бичсэн ч бас хариулна."
    },
]


def match_faq(user_message: str) -> str | None:
    """
    Хэрэглэгчийн мессежийг энгийн keyword-оор шалгаж,
    тохирох FAQ байвал хариуг нь буцаана.
    """
    text = user_message.lower()
    for item in FAQ_LIST:
        if any(kw.lower() in text for kw in item["q_keywords"]):
            return item["answer"]
    return None


def generate_ai_reply(user_message: str) -> str:
    """
    1) Эхлээд FAQ таарах эсэхийг шалгана
    2) Таарахгүй бол OpenAI LLM-ээр ухаалаг хариу гаргана
    """
    # 1. FAQ шалгах
    faq_answer = match_faq(user_message)
    if faq_answer:
        return faq_answer

    # 2. AI хариу
    system_prompt = """
You are an AI assistant for a Mongolian small business Facebook Page.

Business info (та өөрийн дагуу засаарай):
- Нэр: DIY BOOM
- Төрөл: Гар урлал, DIY материал, бэлэг дурсгал
- Байршил: Улаанбаатар, Монгол
- Ажиллах цаг: Даваа–Ням 10:00–20:00
- Хүргэлт: УБ дотор хүргэлттэй

Rules:
- Хэрэглэгчид ЗӨВХӨН монголоор, энгийн найрсаг, богино хариу өг.
- Гол санааг товч, ойлгомжтой хэл. 2–4 өгүүлбэр байхад хангалттай.
- Мэдэхгүй мэдээллийг битгий зохио, "яг одоо надад энэ мэдээлэл байхгүй байна" гэж шулуухан хэл.
- Худалдааны үед соёлтойгоор асуулт асууж, хэрэгцээг нь тодруулж бай.
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.6,
    )

    return completion.choices[0].message.content.strip()


# ---------------- Messenger рүү мессеж илгээх ---------------- #

def send_message(recipient_id: str, text: str) -> None:
    """
    Facebook Graph API ашиглан хэрэглэгч рүү текст мессеж илгээнэ.
    """
    url = "https://graph.facebook.com/v24.0/me/messages"

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text},
    }

    response = requests.post(url, params=params, json=payload)

    print("SEND MESSAGE STATUS:", response.status_code, response.text)


# ---------------- Webhook VERIFY (GET) ---------------- #

@app.get("/webhook")
def verify_webhook():
    """
    Facebook-ээс эхний удаа webhook шалгах GET хүсэлт ирэхэд
    VERIFY_TOKEN-оо ашиглаад баталгаажуулна.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED!")
        return challenge, 200

    print("WEBHOOK VERIFICATION FAILED")
    return "Verification failed", 403


# ---------------- Webhook EVENT (POST) ---------------- #

@app.post("/webhook")
def handle_webhook():
    """
    Messenger-ээс ирсэн бүх event (мессеж, постback г.м) энд орж ирнэ.
    Одоогоор зөвхөн text message дээр ажиллана.
    """
    data = request.get_json()
    print("===== NEW EVENT =====")
    print(data)

    if data.get("object") != "page":
        return "Ignored", 404

    for entry in data.get("entry", []):
        for event in entry.get("messaging", []):
            # Мессеж ирсэн бол
            if "message" in event:
                sender_id = event["sender"]["id"]
                message = event["message"]

                # Echo (өөрийн явуулсан мессеж) байвал алгасна
                if message.get("is_echo"):
                    continue

                user_text = message.get("text", "")
                if not user_text:
                    # зургууд г.м ирвэл одоохондоо text байхгүй тул алгасъя
                    continue

                # AI / FAQ хариу гаргах
                reply_text = generate_ai_reply(user_text)

                # Messenger рүү буцааж илгээх
                send_message(sender_id, reply_text)

    return "EVENT_RECEIVED", 200


# ---------------- Main ---------------- #

if __name__ == "__main__":
    # Локал дээр ажиллуулах порт
    app.run(port=5000, debug=True)
