import streamlit as st
import re
import random
import os
import json
import hashlib
import secrets
import smtplib
import base64
from io import BytesIO
from email.message import EmailMessage
from datetime import datetime, timedelta
import requests
import sympy as sp
from PIL import Image, ImageOps
from urllib.parse import quote
st.set_page_config(page_title="ApexBot Ultra AI", page_icon="🤖", layout="centered")

USER_DB_FILE = "users.json"

def load_user_db():
    try:
        with open(USER_DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_db(user_db):
    with open(USER_DB_FILE, "w", encoding="utf-8") as file:
        json.dump(user_db, file, ensure_ascii=False, indent=2)

def hash_value(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default

def is_placeholder(value):
    return not value or value.startswith("your-") or value == "+10000000000"

def is_universe_question(query):
    universe_terms = [
        "universe", "space", "planet", "star", "galaxy", "galaxies", "black hole",
        "nebula", "cosmos", "solar system", "milky way", "big bang", "astronaut",
        "nasa", "isro", "earth", "moon", "sun", "सूर्य", "चंद्रमा", "ग्रह",
        "तारा", "आकाशगंगा", "ब्रह्मांड", "ब्लैक होल", "अंतरिक्ष",
    ]
    clean_query = query.lower()
    return any(term in clean_query for term in universe_terms)

def is_current_question(query):
    current_terms = [
        "latest", "current", "today", "now", "news", "अभी", "आज", "वर्तमान",
        "नवीनतम", "ताजा", "ताज़ा",
    ]
    clean_query = query.lower()
    return any(term in clean_query for term in current_terms)

def ask_ai_answer(query, conversation_history=None, image_bytes=None, image_mime_type="image/jpeg"):
    api_key = get_secret("OPENAI_API_KEY")
    if is_placeholder(api_key):
        return None
    st.session_state.pop("ai_error", None)
    if is_universe_question(query):
        system_prompt = (
            "You are ApexBot's astronomy and space-science specialist. Answer universe-related "
            "questions using established astronomy and physics. Distinguish confirmed facts from "
            "theories or estimates, include dates or units when useful, and never invent discoveries. "
            "Correct common misconceptions briefly. Infer the intended astronomy topic even when the "
            "user uses spelling mistakes, Hindi-English mixed language, or an indirect question. "
            "For distances between the Sun, Earth, and planets, explain that the distance changes "
            "with orbital position, state whether you are giving an average, closest, farthest, or "
            "date-specific estimate, and give both kilometers and astronomical units (AU) when possible. "
            "Reply in the user's language and explain clearly for a beginner unless the user requests "
            "advanced detail."
        )
    else:
        system_prompt = (
            "You are ApexBot, a helpful general assistant. Analyze the user's question carefully "
            "and answer accurately and clearly. Reply in the user's language. For programming "
            "questions, include a short example when useful. For BCA and other academic questions, "
            "act as a patient tutor: define the concept, explain it step by step, include a simple "
            "example, and mention important differences or exam points when relevant. Cover topics "
            "such as programming, loops, data structures, algorithms, DBMS, operating systems, "
            "computer networks, web development, software engineering, and computer architecture. "
            "Also cover BTech topics such as engineering mathematics, digital logic, electronics, "
            "computer organization, compiler design, theory of computation, artificial intelligence, "
            "machine learning, and technical problem solving. For questions about using apps or "
            "websites, provide numbered step-by-step instructions, mention required login or "
            "permissions, and clearly say when menu names may differ by app version. Do not claim "
            "to access or control the user's account. "
            "For every answer, prioritize correctness over sounding confident. Never guess or "
            "invent facts. If the question is ambiguous, ask one clarifying question. If a fact "
            "may have changed, state the relevant date and say that it needs verification. "
            "If you do not know, clearly say that you do not know."
        )
    messages = [{"role": "system", "content": system_prompt}]
    if conversation_history:
        messages.extend(
            {
                "role": message["role"],
                "content": message["content"],
            }
            for message in conversation_history[-10:]
            if message.get("role") in {"user", "assistant"}
        )
    user_content = query
    if is_current_question(query):
        live_reference = fetch_universal_accurate_answer(query)
        user_content = (
            f"User question: {query}\n\n"
            f"Reference context from Wikipedia (may be incomplete): {live_reference}\n\n"
            "Use the reference carefully, state the date or uncertainty, and do not claim live access "
            "beyond the provided context."
        )
    if image_bytes:
        encoded_image = base64.b64encode(image_bytes).decode("ascii")
        user_content = [
            {"type": "text", "text": user_content},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{image_mime_type};base64,{encoded_image}",
                },
            },
        ]
    messages.append({"role": "user", "content": user_content})
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": get_secret("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": messages,
                "temperature": 0.2,
            },
            timeout=30,
        )
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"].strip()
        return answer or None
    except requests.HTTPError as error:
        if error.response.status_code == 429:
            st.session_state.ai_error = "OpenAI API quota/credits समाप्त हैं या rate limit लग गई है"
        else:
            st.session_state.ai_error = f"OpenAI API HTTP {error.response.status_code}"
        return None
    except requests.RequestException:
        st.session_state.ai_error = "OpenAI API network request failed"
        return None
    except (KeyError, IndexError, TypeError):
        st.session_state.ai_error = "OpenAI API returned an unexpected response"
        return None

def translate_with_ai(query):
    api_key = get_secret("OPENAI_API_KEY")
    if is_placeholder(api_key):
        return None
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": get_secret("OPENAI_MODEL", "gpt-4o-mini"),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a translation engine. Detect the requested target language from "
                            "the user's instruction, translate only the requested text, preserve its "
                            "meaning and tone, and return only the translation without explanations. "
                            "Support any natural language and Hindi-English mixed instructions."
                        ),
                    },
                    {"role": "user", "content": query},
                ],
                "temperature": 0.1,
            },
            timeout=30,
        )
        response.raise_for_status()
        translation = response.json()["choices"][0]["message"]["content"].strip()
        return translation or None
    except (requests.RequestException, KeyError, IndexError, TypeError):
        return None

def send_email_code(email, code):
    smtp_host = get_secret("SMTP_HOST")
    smtp_port = int(get_secret("SMTP_PORT", "587"))
    smtp_user = get_secret("SMTP_USER")
    smtp_password = get_secret("SMTP_PASSWORD")
    if any(is_placeholder(value) for value in [smtp_host, smtp_user, smtp_password]):
        return False, "Email SMTP settings missing"
    message = EmailMessage()
    message["Subject"] = "ApexBot verification code"
    message["From"] = smtp_user
    message["To"] = email
    message.set_content(f"Your ApexBot verification code is: {code}\nIt expires in 10 minutes.")
    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True, ""
    except Exception as error:
        return False, str(error)

def send_sms_code(phone, code):
    account_sid = get_secret("TWILIO_ACCOUNT_SID")
    auth_token = get_secret("TWILIO_AUTH_TOKEN")
    from_phone = get_secret("TWILIO_FROM_PHONE")
    if any(is_placeholder(value) for value in [account_sid, auth_token, from_phone]):
        return False, "SMS provider settings missing"
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
    payload = {
        "From": from_phone,
        "To": phone,
        "Body": f"ApexBot verification code: {code}. Expires in 10 minutes.",
    }
    try:
        response = requests.post(url, data=payload, auth=(account_sid, auth_token), timeout=10)
        response.raise_for_status()
        return True, ""
    except Exception as error:
        return False, str(error)

def send_verification_codes(email, phone):
    code = str(secrets.randbelow(900000) + 100000)
    email_sent, email_error = send_email_code(email, code)
    sms_sent, sms_error = send_sms_code(phone, code)
    if email_sent and sms_sent:
        return code, ""
    demo_mode = str(get_secret("DEMO_MODE", "true")).lower() == "true"
    if demo_mode and email_error == "Email SMTP settings missing" and sms_error == "SMS provider settings missing":
        return code, "DEMO"
    errors = []
    if not email_sent:
        errors.append(f"Email: {email_error}")
    if not sms_sent:
        errors.append(f"SMS: {sms_error}")
    return None, " | ".join(errors)

def start_code_flow(email, phone, purpose):
    code, error = send_verification_codes(email, phone)
    if code is None:
        return False, error
    st.session_state[f"{purpose}_pending"] = {
        "email": email,
        "phone": phone,
        "code_hash": hash_value(code),
        "expires_at": (datetime.now() + timedelta(minutes=10)).isoformat(),
    }
    if error == "DEMO":
        st.session_state[f"{purpose}_demo_code"] = code
    return True, ""

if "user_db" not in st.session_state:
    st.session_state.user_db = load_user_db()
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if st.session_state.logged_in_user is None:
    st.title("🔐 Welcome to ApexBot AI")
    auth_mode = st.tabs(["🔑 Login", "📝 Sign Up (Create ID)", "♻️ Recover ID"])
    with auth_mode[1]:
        st.subheader("Create a New Account")
        new_name = st.text_input("Full Name", key="reg_name")
        new_email = st.text_input("Email Address", key="reg_email")
        new_phone = st.text_input("Mobile Number", key="reg_phone")
        new_pass = st.text_input("Create Password", type="password", key="reg_pass")
        
        if st.button("Send verification code", key="send_registration_code"):
            name = new_name.strip()
            email = new_email.strip().lower()
            phone = new_phone.strip()
            missing_fields = [
                label for label, value in [
                    ("Full Name", name),
                    ("Email Address", email),
                    ("Mobile Number", phone),
                    ("Create Password", new_pass),
                ] if not value
            ]
            if missing_fields:
                st.warning(f"⚠️ इन fields को भरें: {', '.join(missing_fields)}")
            elif not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
                st.warning("⚠️ सही email address डालें।")
            elif len(new_pass) < 8:
                st.warning("⚠️ Password कम से कम 8 characters का होना चाहिए।")
            elif email in st.session_state.user_db:
                st.error("❌ यह ईमेल आईडी पहले से रजिस्टर्ड है!")
            else:
                success, error = start_code_flow(email, phone, "registration")
                if success:
                    st.session_state.registration_details = {
                        "name": name,
                        "email": email,
                        "phone": phone,
                        "password_hash": hash_value(new_pass),
                    }
                    st.success("OTP email और mobile number दोनों पर भेज दिया गया है।")
                    if st.session_state.get("registration_demo_code"):
                        st.info(f"Demo Mode OTP: {st.session_state.registration_demo_code}")
                else:
                    st.error(f"OTP भेजा नहीं जा सका: {error}")

        registration_pending = st.session_state.get("registration_pending")
        if registration_pending and st.session_state.get("registration_details"):
            registration_code = st.text_input("Email और mobile पर मिला OTP", key="registration_code")
            if st.button("Verify and create account", key="verify_registration"):
                expired = datetime.now() > datetime.fromisoformat(registration_pending["expires_at"])
                valid_code = hash_value(registration_code.strip()) == registration_pending["code_hash"]
                if not expired and valid_code:
                    details = st.session_state.registration_details
                    st.session_state.user_db[details["email"]] = {
                        "name": details["name"],
                        "phone": details["phone"],
                        "password_hash": details["password_hash"],
                    }
                    save_user_db(st.session_state.user_db)
                    del st.session_state.registration_pending
                    del st.session_state.registration_details
                    st.session_state.pop("registration_demo_code", None)
                    st.success("🎉 Email और mobile verify हो गए। अब Login करें।")
                else:
                    st.error("OTP गलत है या expire हो चुका है।")

    with auth_mode[0]:
        st.subheader("Login to your Account")
        login_email = st.text_input("Email Address", key="log_email")
        login_pass = st.text_input("Password", type="password", key="log_pass")
        
        if st.button("Login"):
            account = st.session_state.user_db.get(login_email.strip().lower())
            if account and account.get("password_hash") == hash_value(login_pass):
                st.session_state.logged_in_user = account["name"]
                st.rerun()
            else:
                st.error("❌ गलत ईमेल या पासवर्ड! कृपया दोबारा जांचें।")

    with auth_mode[2]:
        st.subheader("Recover your account")
        recovery_email = st.text_input("Registered Email Address", key="recovery_email")
        recovery_phone = st.text_input("Registered Mobile Number", key="recovery_phone")
        if st.button("Send recovery code", key="send_recovery_code"):
            email = recovery_email.strip().lower()
            phone = recovery_phone.strip()
            account = st.session_state.user_db.get(email)
            if account and account.get("phone") == phone:
                success, error = start_code_flow(email, phone, "recovery")
                if success:
                    st.success("Recovery OTP email और mobile number दोनों पर भेज दिया गया है।")
                    if st.session_state.get("recovery_demo_code"):
                        st.info(f"Demo Mode OTP: {st.session_state.recovery_demo_code}")
                else:
                    st.error(f"OTP भेजा नहीं जा सका: {error}")
            else:
                st.error("Email और mobile number match नहीं करते।")

        recovery_pending = st.session_state.get("recovery_pending")
        if recovery_pending:
            recovery_code = st.text_input("Email और mobile पर मिला OTP", key="recovery_code")
            reset_password = st.text_input("New Password", type="password", key="reset_password")
            confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_password")
            if st.button("Verify and reset password", key="verify_recovery"):
                expired = datetime.now() > datetime.fromisoformat(recovery_pending["expires_at"])
                valid_code = hash_value(recovery_code.strip()) == recovery_pending["code_hash"]
                if expired:
                    st.error("OTP expire हो चुका है। नया recovery code भेजें।")
                elif not valid_code:
                    st.error("OTP गलत है।")
                elif len(reset_password) < 8:
                    st.error("Password कम से कम 8 characters का होना चाहिए।")
                elif reset_password != confirm_password:
                    st.error("दोनों passwords समान नहीं हैं।")
                else:
                    st.session_state.user_db[recovery_pending["email"]]["password_hash"] = hash_value(reset_password)
                    save_user_db(st.session_state.user_db)
                    del st.session_state.recovery_pending
                    st.session_state.pop("recovery_demo_code", None)
                    st.success("Password बदल गया। अब Login करें।")
                
    st.stop() 
st.title("🤖 ApexBot Ultra AI Platform")
st.write(f"👋 Welcome, *{st.session_state.logged_in_user}*!")

ACADEMIC_DATABASE = {
    "math formulas": "📐 *Math Formula Bank:*\n• Algebra: (a + b)² = a² + 2ab + b²\n• Calculus: d/dx(xⁿ) = n·xⁿ⁻¹ | ∫ xⁿ dx = (xⁿ⁺¹) / (n + 1)"
}
SHAYARI_COLLECTION = {
    "sad": ["दिल से रोए मगर होठों से मुस्कुरा बैठे,\nबड़ी सादगी से हम उनसे दिल्लगी कर बैठे।"],
    "romantic": ["धड़कन मेरी तुमसे है, सांसें मेरी तुमसे हैं,\nतुम्हें कैसे बताएं कि हमारी जिंदगी तुमसे है।"],
    "motivation": ["मंजिलें उन्हीं को मिलती हैं जिनके सपनों में जान होती है,\nपंखों से कुछ नहीं होता, हौसलों से उड़ान होती है।"],
    "funny": ["दिल में कोई gam नहीं, कॉलेज में हम किसी से कम नहीं!"]
}
BOT_RULES = {
    r'\b(hello|hi|hey)\b': "Hello! How can I help you today?",
    r'\b(how are you)\b': "I'm doing great, thank you for asking!",
    r'(india ki capital|capital of india|भारत की राजधानी|इंडिया की राजधानी)': (
        "🇮🇳 भारत (India) की राजधानी *नई दिल्ली (New Delhi)* है।"
    ),
    r'\b(what are loops|what is a loop|loops kya hote hain|loops kya hote hai|loop kya hota hai)\b': (
        "🔁 *Loop* programming में किसी काम को बार-बार करने के लिए इस्तेमाल होता है।\n\n"
        "• *for loop:* जब दोहराव की संख्या पता हो।\n"
        "```python\nfor i in range(3):\n    print(i)\n```\n"
        "• *while loop:* जब तक condition सही हो, तब तक चलता है।\n"
        "```python\ni = 0\nwhile i < 3:\n    print(i)\n    i += 1\n```"
    ),
        r'(sun kya hai|suraj kya hai|सूरज क्या है|सूर्य क्या है|what is the sun)': (
            "☀️ *सूर्य (Sun)* हमारे सौरमंडल का केंद्र और एक तारा है। यह मुख्य रूप से hydrogen और helium गैसों से बना है। "
            "सूर्य की रोशनी और गर्मी पृथ्वी पर जीवन के लिए बहुत महत्वपूर्ण हैं। पृथ्वी सूर्य की परिक्रमा लगभग 365 दिनों में करती है।"
        ),
        r'(neel arm strong|neil armstrong|neil arm strong|नील आर्मस्ट्रांग)': (
            "🚀 *Neil Armstrong* एक अमेरिकी astronaut थे। वे 20 जुलाई 1969 को Apollo 11 mission के दौरान "
            "चंद्रमा पर कदम रखने वाले पहले इंसान बने। उनके साथ Buzz Aldrin भी Moon पर उतरे थे।"
        ),
        r'(stdio\.h kya hai|what is stdio\.h|stdio\.h)': (
            "💻 *stdio.h* C programming की standard input/output header file है। इसमें `printf()`, "
            "`scanf()`, ` getchar()`, `putchar()` और file handling से जुड़े functions की declarations होती हैं। "
            "इसे C program में ऐसे include करते हैं:\n\n"
            "```c\n#include <stdio.h>\n\nint main(void) {\n    printf(\"Hello\");\n    return 0;\n}\n```"
        ),
        r'(समाकलन क्या होता है|समाकलन kya hota hai|integral kya hota hai|what is integration)': (
            "📐 *समाकलन (Integration)* calculus की वह प्रक्रिया है जिससे किसी function का antiderivative "
            "या curve के नीचे का area निकाला जाता है। यह differentiation की उल्टी प्रक्रिया है।\n\n"
            "उदाहरण: `∫ x² dx = x³/3 + C`, जहाँ `C` integration constant है।"
        ),
        r'(all planets|all the planets|sabhi grah|saare grah|sare grah|सभी ग्रह|सारे ग्रह)': (
            "🪐 *सौरमंडल के 8 ग्रह (सूर्य से दूरी के क्रम में):*\n\n"
            "1. *बुध (Mercury):* सूर्य के सबसे पास और सबसे छोटा ग्रह।\n"
            "2. *शुक्र (Venus):* सबसे गर्म ग्रह और घना atmosphere।\n"
            "3. *पृथ्वी (Earth):* liquid water और ज्ञात जीवन वाला ग्रह।\n"
            "4. *मंगल (Mars):* लाल ग्रह; इसकी सतह पर iron oxide के कारण लाल रंग है।\n"
            "5. *बृहस्पति (Jupiter):* सबसे बड़ा ग्रह; Great Red Spot इसका विशाल storm है।\n"
            "6. *शनि (Saturn):* अपने स्पष्ट और बड़े rings के लिए प्रसिद्ध।\n"
            "7. *अरुण (Uranus):* अपनी धुरी पर लगभग sideways घूमने वाला ice giant।\n"
            "8. *वरुण (Neptune):* सूर्य से सबसे दूर का 8वाँ ग्रह और बहुत तेज हवाओं वाला ice giant।\n\n"
            "💡 बुध, शुक्र, पृथ्वी और मंगल rocky planets हैं; बृहस्पति और शनि gas giants, "
            "जबकि अरुण और वरुण ice giants हैं। Pluto को 2006 से dwarf planet माना जाता है।"
        ),
    r'\b(govt job link|sarkari result)\b': "Sarkari Result: https://sarkariresult.com",
    r'\b(scholarship link)\b': "National Scholarship Portal: https://scholarships.gov.in",
}
def fetch_universal_accurate_answer(query):
    clean_query = query.lower().strip()
    if "mind" in clean_query and "part" in clean_query:
        return ("🧠 *Human Brain Structure:\n1. **Forebrain:* Cerebrum (Thinking, Memory), Thalamus.\n2. *Midbrain:* Controls eye and hearing reflexes.\n3. *Hindbrain:* Cerebellum (Balance), Medulla.")
    try:
        headers = {'User-Agent': 'UniversalAppBot/1.0'}
        search_response = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": 1,
            },
            headers=headers,
            timeout=5,
        )
        search_response.raise_for_status()
        search_results = search_response.json().get("query", {}).get("search", [])
        if not search_results:
            return f"📝 मुझे '{query}' के लिए जानकारी नहीं मिली। कृपया सवाल को थोड़ा स्पष्ट लिखें।"

        article_title = search_results[0]["title"]
        query_words = set(re.findall(r"[a-zA-Z0-9]+", query.lower()))
        title_words = set(re.findall(r"[a-zA-Z0-9]+", article_title.lower()))
        meaningful_words = query_words - {
            "what", "is", "are", "the", "a", "an", "of", "in", "on", "for",
            "how", "why", "who", "what", "kya", "hai", "ke", "ki", "ka",
        }
        if meaningful_words and not meaningful_words.intersection(title_words):
            return f"📝 मुझे '{query}' के लिए भरोसेमंद जानकारी नहीं मिली।"
        summary_response = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(article_title.replace(' ', '_'))}",
            headers=headers,
            timeout=5,
        )
        summary_response.raise_for_status()
        extract = summary_response.json().get("extract", "")
        if extract:
            return f"✨📚 *Universal Knowledge Base ({article_title}):*\n\n{extract}"
        return f"📝 '{query}' के लिए article मिला, लेकिन उसका summary उपलब्ध नहीं है।"
    except Exception:
        return "❌ जानकारी service अभी उपलब्ध नहीं है। बाद में फिर कोशिश करें।"

def solve_math_question(expression_str):
    expression = re.sub(
        r'^\s*(what is|calculate|solve|find|evaluate|गणना करो|हल करो)\s+',
        '',
        expression_str,
        flags=re.IGNORECASE,
    ).strip()
    expression = re.sub(r'\s*(kitne hote hain|kitne hote hai|कितने होते हैं|कितने होते है)\s*$', '', expression, flags=re.IGNORECASE).strip()
    expression = re.sub(r'\bplus\b|\bजोड़\b|\bजोड़ो\b', '+', expression, flags=re.IGNORECASE)
    expression = re.sub(r'\bminus\b|\bघटा\b|\bघटाओ\b', '-', expression, flags=re.IGNORECASE)
    expression = re.sub(r'\b(do|दो)\b', '2', expression, flags=re.IGNORECASE)
    expression = re.sub(r'\b(ek|एक)\b', '1', expression, flags=re.IGNORECASE)
    expression = re.sub(r'\b(teen|तीन)\b', '3', expression, flags=re.IGNORECASE)
    expression = re.sub(r'\b(chaar|चार)\b', '4', expression, flags=re.IGNORECASE)
    clean_expr = expression.lower().replace(' ', '')
    try:
        x, y = sp.symbols('x y')
        if "diff" in clean_expr or "derivative" in clean_expr:
            expr_to_solve = re.sub(r'(diff|derivative|of)', '', expression, flags=re.IGNORECASE).strip()
            return f"📐 *Derivative:* d/dx({expr_to_solve}) = {sp.diff(sp.sympify(expr_to_solve), x)}"
        elif any(word in clean_expr for word in ["integrate", "integration", "integral"]):
            expr_to_solve = re.sub(r'(integrate|integration|integral|of)', '', expression, flags=re.IGNORECASE).strip()
            return f"📐 *Integration:* ∫({expr_to_solve})dx = {sp.integrate(sp.sympify(expr_to_solve), x)} + C"
        elif "=" in expression:
            parts = expression.split('=', maxsplit=1)
            return f"📐 *Equation:* x = {sp.solve(sp.Eq(sp.sympify(parts[0]), sp.sympify(parts[1])), x)}"
        else:
            parsed = sp.sympify(expression)
            result = parsed.evalf() if parsed.is_number else sp.simplify(parsed)
            return f"📐 *Result:* {result}"
    except Exception:
        return f"📐 यह valid math expression नहीं है: '{expression_str}'. उदाहरण: 2 + 2"

def is_math_question(query):
    clean_query = query.lower().strip()
    math_words = [
        "calculate", "solve", "evaluate", "derivative", "diff", "integral",
        "integrate", "integration", "equation", "गणना", "अवकलन", "समाकलन",
    ]
    has_expression = bool(re.search(r"\d|[+*/=^()]|\b(x|y|sin|cos|tan|log)\b", clean_query))
    return any(word in clean_query for word in math_words) or has_expression

def translate_text(text, source_lang, target_lang):
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": source_lang,
            "tl": target_lang,
            "dt": "t",
            "q": text,
        }
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200: return "".join([part[0] for part in response.json()[0] if part[0]])
    except Exception: return "❌ अनुवाद एरर।"

def analyze_image_ai(image):
    api_key = get_secret("OPENAI_API_KEY")
    if not is_placeholder(api_key):
        try:
            image_buffer = BytesIO()
            image.convert("RGB").save(image_buffer, format="JPEG", quality=85)
            image_data = base64.b64encode(image_buffer.getvalue()).decode("ascii")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": get_secret("OPENAI_MODEL", "gpt-4o-mini"),
                    "messages": [
                        {
                            "role": "system",
                            "content": "Describe images accurately. Mention visible objects, scene, text, and uncertainty. Reply in the user's likely language.",
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analyze this image in detail."},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                                },
                            ],
                        },
                    ],
                    "temperature": 0.2,
                },
                timeout=45,
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"].strip()
            if answer:
                return f"👁️ *ApexBot AI Image Analysis:*\n\n{answer}"
        except (requests.RequestException, KeyError, IndexError, TypeError):
            st.session_state.ai_error = "Image vision request failed"

    return (
        "👁️ *ApexBot AI Image Analysis Report:*\n\n"
        f"✅ *फाइल डिटेक्शन:* छवि सफलतापूर्वक लोड हो गई है (Dimensions: {image.size[0]}x{image.size[1]} pixels)।\n"
        "ℹ️ वास्तविक object पहचान के लिए valid OpenAI API key और vision-capable model जरूरी है।\n\n"
        "💡 नोट: यदि आप इस इमेज को 'Black & White' करना या 'Rotate' करना चाहते हैं, तो बाईं ओर स्थित साइडबार 'Image Studio' का उपयोग करें!"
    )

def get_bot_response(user_input, conversation_history=None, image_bytes=None, image_mime_type="image/jpeg"):
    clean_input = user_input.lower().strip()
    translation_words = [
        "translate", "translation", "अनुवाद", "में बदलो", "me badlo", "me translate",
        "language me", "भाषा में",
    ]
    if any(word in clean_input for word in translation_words):
        ai_translation = translate_with_ai(user_input)
        if ai_translation:
            return f"🗣️ *Translation:* {ai_translation}"
    if "iski hindi do" in clean_input:
        text = re.sub(r'(iski hindi do)', '', user_input, flags=re.IGNORECASE).strip()
        return f"🗣️ *हिंदी:* {translate_text(text, 'en', 'hi')}"
    if "iski english do" in clean_input:
        text = re.sub(r'(iski english do)', '', user_input, flags=re.IGNORECASE).strip()
        return f"🗣️ *English:* {translate_text(text, 'hi', 'en')}"
    for pattern, response in BOT_RULES.items():
        if re.search(pattern, clean_input):
            return response
    if (
        "math formula" in clean_input
        or "maths formula" in clean_input
        or "mathe ke formule" in clean_input
        or "गणित के सूत्र" in clean_input
    ):
        return ACADEMIC_DATABASE["math formulas"]
    if is_math_question(user_input) and not is_universe_question(user_input):
        return solve_math_question(user_input)
    ai_answer = ask_ai_answer(user_input, conversation_history, image_bytes, image_mime_type)
    if ai_answer:
        return f"🤖 *ApexBot AI:*\n\n{ai_answer}"
    for key, value in ACADEMIC_DATABASE.items():
        if key in clean_input: return value
    if any(k in clean_input for k in ["shayari", "motivation"]):
        c = "sad" if "sad" in clean_input else "romantic" if "romantic" in clean_input else "funny" if "funny" in clean_input else "motivation"
        return f"✨\n{random.choice(SHAYARI_COLLECTION[c])}"
    if st.session_state.get("ai_error"):
        return "⚠️ AI service अभी उपलब्ध नहीं है। API quota/credits check करें; गलत अनुमान दिखाने के बजाय यह सवाल बाद में दोबारा पूछें।"
    return fetch_universal_accurate_answer(user_input)

# --- 6. SIDEBAR MANAGEMENT (IMAGE STUDIO & USER LOGOUT) ---
st.sidebar.header(f"👤 {st.session_state.logged_in_user}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("📸 AI Image Studio & Analyzer")
uploaded_file = st.sidebar.file_uploader("Upload any image here", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    user_img = Image.open(uploaded_file)
    st.session_state.uploaded_image_bytes = uploaded_file.getvalue()
    st.session_state.uploaded_image_mime_type = uploaded_file.type or "image/jpeg"
    st.sidebar.image(user_img, caption="Uploaded Image", use_container_width=True)
    
    if st.sidebar.button("Analyze Image 🔍"):
        analysis_report = analyze_image_ai(user_img)
        st.info(analysis_report)
        
    edit_option = st.sidebar.selectbox("Edit Tools:", ["None", "Black & White", "Rotate 90°", "Resize"])
    if st.sidebar.button("Process Image ⚙️"):
        if edit_option == "Black & White": res = ImageOps.grayscale(user_img)
        elif edit_option == "Rotate 90°": res = user_img.rotate(90, expand=True)
        elif edit_option == "Resize": res = user_img.resize((300, 300))
        if edit_option != "None": st.sidebar.image(res, caption="Edited Image", use_container_width=True)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "नमस्ते! मैं आपका ऑल-इन-वन सुपर एआई असिस्टेंट हूँ। अब आप साइडबार में इमेज अपलोड करके 'Analyze Image' बटन दबाकर मुझसे उसे स्कैन भी करवा सकते हैं!"}]

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("अपना सवाल लिखें..."):
    previous_messages = list(st.session_state.messages)
    st.session_state.messages.append({"role": "user", "content": prompt})
    response = get_bot_response(
        prompt,
        previous_messages,
        st.session_state.get("uploaded_image_bytes"),
        st.session_state.get("uploaded_image_mime_type", "image/jpeg"),
    )
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()