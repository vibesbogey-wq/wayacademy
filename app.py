import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from openai import OpenAI

# ================ ENV АЧААЛЛАХ ================ #
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY байхгүй байна!")

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# ================ ХӨТӨЛБӨРҮҮДИЙН ДАТА ================ #
COURSE_DATA = [
    {
        "course_name": "Стратегийн Дижитал Маркетер",
        "keywords": [
            "стратегийн дижитал маркетер", "digital marketer", "дижитал маркетинг",
            "маркетингийн хөтөлбөр", "маркетер", "facebook сурталчилгаа",
            "instagram сурталчилгаа", "seo", "blue ocean", "facebook ads", "meta ads"
        ],
        "description": (
            "Таамаглахаа боль, үр дүнг удирд! Энэ хөтөлбөр нь карьераа эхлүүлэх, "
            "бизнесээ өсгөх зорилготой хүн бүрт зориулагдсан.\n\n"
            "Бид танд зөвхөн 'Boost' дарахыг заахгүй. Харин стратегийн ахисан түвшний шинжилгээ, "
            "Blue Ocean Strategy, шилдэг маркетингийн стратеги боловсруулах ур чадвар, "
            "Facebook / Instagram сурталчилгааны ахисан түвшний техникүүд, үнэ цэнтэй контент "
            "бүтээх урлагаас эхлээд SEO хүртэл дижитал маркетингийн цогц ур чадварыг эзэмшүүлнэ.\n\n"
            "Төгсөөд:\n"
            "• Meta олон улсын сертификат + Blockchain баталгаажсан мэргэжлийн сертификат\n"
            "• Бодит төсөл дээр ажиллаж орлого олж эхлэх боломж"
        ),
        "teacher": "Э. Энхзаяа (Way Academy-ийн үүсгэн байгуулагч, CEO)",
        "duration": "5 сар (7 хоногт 2 удаа)",
        "schedule": {
            "evening": "Оройн анги: Мягмар, Пүрэв 18:00–21:00",
            "daytime": "Өдрийн анги: Лхагва, Бямба 14:00–17:00"
        },
        "cta": "phone"
    },
    {
        "course_name": "Data Analyst",
        "keywords": [
            "data analyst", "дата аналитик", "өгөгдлийн шинжээч",
            "өгөгдөл", "аналист", "python", "google сертификат", "google data analytics"
        ],
        "description": (
            "Өгөгдлийн шинжээчийн мэргэжил эзэмшүүлэх 100% ажлын байртай хөтөлбөр.\n\n"
            "• Олон улсад зөвшөөрөгдөх Google-н сертификат болон мэргэжлийн хосолсон сертификаттай\n"
            "• Өгөгдөл боловсруулж шинжлэх, үр дүнг тайлагнах аргачлалуудыг суралцана\n"
            "• Python программ дээр дата аналитикийн ахисан түвшний хэрэгслүүдийг практикт ашиглаж сурна\n"
            "• Түнш компаниудын төсөл дээр дадлага хийж, төгсөөд шууд ажлын байранд зуучлуулах боломжтой"
        ),
        "teacher": "Ч. Алтан-Өлзий (Data Analyst-ийн мастер багш)",
        "duration": "4 сар",
        "price": {
            "full": "5,842,000₮",
            "discount": "5,242,000₮",
            "discount_until": "Final Chance (8 сарын 31 хүртэл)"
        },
        "cta": "phone"
    },
    {
        "course_name": "IT Business Analyst",
        "keywords": [
            "it business analyst", "ит бизнес аналист", "бизнес аналист",
            "business analyst", "ба бизнес шинжээч", "it ба", "ба"
        ],
        "description": (
            "IT Business Analyst мэргэжил эзэмшүүлэх 100% ажлын байртай хөтөлбөр.\n\n"
            "Технологи болон бизнесийн мэдлэг, ур чадварыг цогцлоосон мэргэжилтэн болж "
            "хөдөлмөрийн зах зээлд давамгайлна."
        ),
        "teacher": "Т. Батзаяа (Технологи хариуцсан захирал, мастер багш)",
        "duration": "3 сар",
        "cta": "phone"
    },
    {
        "course_name": "Project Zero: AI Agent Developer",
        "keywords": [
            "project zero", "ai agent", "ai agent developer", "code the future",
            "agent developer", "ai developer", "архитектор", "ai агент", "projectzero"
        ],
        "description": (
            "Project Zero: Code the Future нь таныг AI хэрэглэгчээс AI бүтээгч 'Архитектор' болгон хувиргах "
            "онцгой 4 сарын аялал юм.\n\n"
            "Элсэлт нь тусгай, зөвхөн өргөдлөөр, цөөн тооны анхдагчдыг сонгон шалгаруулдаг."
        ),
        "teacher": "З. Батзаяа (Project Zero, IT Business Analyst-ийн мастер багш)",
        "duration": "4 сар",
        "price": {
            "full": "7,448,000₮",
            "discount": "6,640,000₮",
            "discount_until": "9 сарын 14 хүртэл"
        },
        "application_link": "https://forms.gle/qgyNEKecuJ22f5mYA",
        "cta": "application"
    },
]

# ================ FAQ ================ #
FAQ_LIST = [
    {
        "q_keywords": ["хөтөлбөр", "ямар хөтөлбөр", "course", "program", "сургалт", "танайд"],
        "answer": (
            "Бидэнд одоо эдгээр топ хөтөлбөрүүд явагдаж байна:\n\n"
            "1️⃣ Стратегийн Дижитал Маркетер\n"
            "2️⃣ Data Analyst (Google сертификаттай)\n"
            "3️⃣ IT Business Analyst\n"
            "4️⃣ Project Zero: AI Agent Developer (Өргөдөлтэй)\n\n"
            "Аль нь сонирхож байна вэ? 😊"
        ),
    },
    {
        "q_keywords": ["онцлог", "ялгарал", "way academy юу", "яагаад way", "та нар юу"],
        "answer": (
            "Way Academy ялгарах онцлогууд:\n\n"
            "✨ C-level багш нар (CEO, CTO, CDO)\n"
            "✨ Бодит төсөл дээр ажилладаг\n"
            "✨ 100% ажлын байрны баталгаа (зарим хөтөлбөрт)\n"
            "✨ AI-г бүх сургалтдаа нэвтрүүлсэн\n"
            "✨ Төгссөн ч гэсэн тасралтгүй дэмжинэ 💪\n\n"
            "Зөв газарт ирлээ шүү! 🎯"
        ),
    },
    {
        "q_keywords": ["утас", "холбогдох", "contact", "phone", "залгах", "дугаар"],
        "answer": "📞 Холбогдох утас: 9920-1187\n✉ Email: hello@wayconsulting.io\n\nЯг одоо залгаад зөвлөгөө аваарай 😊",
    },
]

# ================ ТУСЛАХ ФУНКЦУУД ================ #

def match_course_info(user_message: str) -> dict | None:
    msg = user_message.lower().strip()
    for course in COURSE_DATA:
        if any(keyword.lower() in msg for keyword in course["keywords"]):
            txt = f"**{course['course_name']}**\n\n"
            txt += course["description"] + "\n\n"
            txt += f"👨‍🏫 Багш: {course['teacher']}\n"
            txt += f"⏳ Хугацаа: {course['duration']}\n"

            price = course.get("price")
            if price and price.get("discount"):
                txt += f"\n💰 Хөнгөлөлттэй үнэ: {price['discount']}\n"
                if price.get("discount_until"):
                    txt += f"⏰ {price['discount_until']}\n"

            return {
                "reply": txt,
                "cta": course.get("cta", "phone"),
                "course_name": course["course_name"]
            }
    return None


def match_faq(user_message: str) -> str | None:
    text = user_message.lower()
    for item in FAQ_LIST:
        if any(kw.lower() in text for kw in item["q_keywords"]):
            return item["answer"]
    return None


def generate_ai_reply(user_message: str, user_id: str = None) -> dict:
    # 1. Курсын мэдээлэл
    course_match = match_course_info(user_message)
    if course_match:
        return course_match

    # 2. FAQ
    faq_answer = match_faq(user_message)
    if faq_answer:
        return {"reply": faq_answer, "cta": "phone"}

    # 3. GPT хариу (хэрвээ юу ч таараагүй бол)
    system_prompt = """
Та Way Academy-ийн найрсаг, хурдан, ойр дотно AI туслах юм. Зөвхөн монголоор хариулна.

Хэрэглэгчийг гайхшруулж, тусалж, хөтөлбөр рүү чиглүүлэх ёстой.
Хариу: 2-4 өгүүлбэр, 1-2 emoji, асуулт тавьж тодруулна.
"Гайхалтай!", "Зөв газарт ирлээ!", "Яг одоо элсэх боломжтой шүү" гэх мэт.

Хэрэв мэдэхгүй бол: "99201187 руу залгаад багш нараас шууд асуугаарай 😊"

Хөтөлбөрүүд:
1. Стратегийн Дижитал Маркетер
2. Data Analyst (Google сертификат)
3. IT Business Analyst
4. Project Zero: AI Agent Developer (өргөдөлтэй элсэлт)

Утас: 99201187 | hello@wayconsulting.io
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.8,
            max_tokens=300
        )

        reply = completion.choices[0].message.content.strip()

        # Хэрэв Project Zero яригдаж байвал application CTA буцаах
        cta = "phone"
        if any(kw in user_message.lower() for kw in ["project zero", "ai agent", "архитектор", "code the future"]):
            cta = "application"

        return {
            "reply": reply,
            "cta": cta,
            "metadata": {"model": "gpt-4o-mini", "user_id": user_id},
        }

    except Exception as e:
        print(f"OpenAI Error: {e}")
        return {
            "reply": "Уучлаарай, одоо жаахан техникийн асуудал гарлаа 😅\nЯг одоо 99201187 руу залгаарай, багш нар таныг хүлээж байна!",
            "cta": "phone",
        }


# ================ MANYCHAT ENDPOINT ================ #

@app.route("/manychat-ai", methods=["POST"])
def manychat_ai():
    try:
        data = request.get_json()
        user_message = data.get("user_message", "").strip()
        user_id = data.get("user_id", "unknown")
        user_name = data.get("user_name", "Хэрэглэгч")

        if not user_message:
            return jsonify({
                "reply": f"Сайн байна уу {user_name.split()[0] if user_name else ''}! 😊\nWay Academy-д тавтай морил!\nТанд ямар хөтөлбөр сонирхолтой вэ?",
                "cta_type": "none"
            })

        result = generate_ai_reply(user_message, user_id)

        response = {
            "reply": result["reply"],
            "cta_type": result.get("cta", "phone"),
            "course_name": result.get("course_name", ""),
        }

        print(f"[{user_id}] {user_name}: {user_message}")
        print(f"→ Reply: {result['reply'][:120]}... | CTA: {response['cta_type']}")

        return jsonify(response), 200

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return jsonify({
            "reply": "Уучлаарай, алдаа гарлаа 😅\nТа 99201187 руу шууд залгаарай, бид таныг хүлээж байна!",
            "cta_type": "phone"
        }), 500


# ================ HEALTH CHECK ================ #

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "running",
        "service": "Way Academy AI Assistant",
        "version": "2.0",
        "endpoints": ["/manychat-ai"]
    }), 200


# ================ MAIN ================ #

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)