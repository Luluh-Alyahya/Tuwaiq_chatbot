import streamlit as st
import random, re, base64, math, datetime
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent         
CANDIDATE_DIRS = [
    BASE_DIR / "images",                          
    (BASE_DIR / ".." / "images").resolve(),         
]

def resolve_image(*parts) -> Path | None:
    for d in CANDIDATE_DIRS:
        p = d / Path(*parts)
        if p.exists():
            return p
    return None

def img_to_base64(path: Path | str) -> str | None:
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

# ================== Initialize session state ==================
st.set_page_config(
    page_title="مساعد أكاديمية طويق 🎓",
    layout="wide",
    page_icon="🤖"
)

# ================== Initialize session state ==================
if "history" not in st.session_state:
    # history عناصرها: (sender, message, ts) — لو كان كودك القديم بدون ts بيشتغل برضه
    st.session_state.history = []
if "last_input" not in st.session_state:
    st.session_state.last_input = ""
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False

# === Attendance calculator session state ===
if "attn_mode" not in st.session_state:
    st.session_state.attn_mode = False
if "attn_absences" not in st.session_state:
    st.session_state.attn_absences = None
if "attn_total_days" not in st.session_state:
    st.session_state.attn_total_days = None
if "attn_awaiting" not in st.session_state:
    st.session_state.attn_awaiting = None  # "absences" or "weeks"

# === Assets ===
logo_path = resolve_image("map.png") 
if not logo_path:
    st.error("error.")
# ================== Utils ==================
def now_str():
    return datetime.datetime.now().strftime("%H:%M")

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return None

#  Attendance parsing & logic 
def parse_int_from_text(text: str) -> int | None:
    arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    t = text.translate(arabic_digits)

    patterns = [
        r"(?<!\d)(\d+)\s*(?:يوم|أيام|day|days)\b",
        r"(?:غبت|غيابي|غياب|missed|absence)\D*?(\d+)",
        r"(?<!\d)(\d+)(?!\d)",  # fallback
    ]
    for pat in patterns:
        m = re.search(pat, t, flags=re.IGNORECASE)
        if m:
            try:
                return int(m.group(1))
            except ValueError:
                continue
    return None

def days_left_for_cert(total_days: int, absences: int):
    if total_days <= 0:
        return {
            "required_attendance": 0,
            "max_absences": 0,
            "remaining_can_miss": 0,
            "attendance_percent": 0.0,
            "eligible_now": False,
            "over_by": 0
        }
    required_attendance = math.ceil(0.90 * total_days)
    max_absences = total_days - required_attendance

    absences = max(0, absences)
    current_attendance = max(0, total_days - absences)
    attendance_percent = round((current_attendance / total_days) * 100, 2)

    remaining_can_miss = max_absences - absences
    eligible_now = remaining_can_miss >= 0
    over_by = abs(remaining_can_miss) if remaining_can_miss < 0 else 0

    return {
        "required_attendance": required_attendance,
        "max_absences": max_absences,
        "remaining_can_miss": max(0, remaining_can_miss),
        "attendance_percent": attendance_percent,
        "eligible_now": eligible_now,
        "over_by": over_by
    }

def should_start_attendance_flow(text: str) -> bool:
    triggers = [
        r"(حساب|احسب|أهلية|الشهادة|شهادة).*(90|٩٠).*?(حضور|attendance)",
        r"(حساب|احسب).*(شهادة|حضور)",
        r"(attendance|certificate).*(90)",
    ]
    t = text.strip()
    for pat in triggers:
        if re.search(pat, t, flags=re.IGNORECASE):
            return True
    if t in {"حساب الشهادة", "احسب الشهادة", "حساب حضور","حساب الغياب" ,"احسب الغياب" , "attendance", "cert"}:
        return True
    return False

def handle_attendance_flow(user_input):
    if should_start_attendance_flow(user_input):
        st.session_state.attn_mode = True
        st.session_state.attn_awaiting = "weeks"
        st.session_state.attn_absences = None
        st.session_state.attn_total_days = None
        return "حاسبة أهلية الحصول على الشهادة (90% حضور) 📊\n\nكم عدد أسابيع المعسكر أو البرنامج؟\n(مثال: 6 أسابيع)"

    if st.session_state.attn_mode:
        if st.session_state.attn_awaiting == "weeks":
            total_weeks = parse_int_from_text(user_input)
            if total_weeks and total_weeks > 0:
                total_days = total_weeks * 5  # كل أسبوع = 5 أيام
                st.session_state.attn_total_days = total_days
                st.session_state.attn_awaiting = "absences"
                return f"ممتاز! إجمالي أيام البرنامج: {total_days} يوم (حُسب من {total_weeks} أسابيع)\n\nكم عدد أيام الغياب؟"
            else:
                return "لم أتمكن من فهم عدد الأسابيع. يرجى كتابة الرقم بوضوح\n(مثال: 6 أسابيع)"

        elif st.session_state.attn_awaiting == "absences":
            absences = parse_int_from_text(user_input)
            if absences is not None and absences >= 0:
                st.session_state.attn_absences = absences
                result = days_left_for_cert(st.session_state.attn_total_days, absences)

                st.session_state.attn_mode = False
                st.session_state.attn_awaiting = None

                response = f"""🔢 **المعلومات الأساسية:**
• إجمالي أيام البرنامج: {st.session_state.attn_total_days} يوم
• أيام الغياب: {absences} يوم
• نسبة الحضور الحالية: {result['attendance_percent']}%

📋 **متطلبات الشهادة (90%)**:
• الحد الأدنى للحضور: {result['required_attendance']} يوم
• الحد الأقصى للغياب المسموح: {result['max_absences']} يوم
"""
                if result['eligible_now']:
                    response += f"""✅ **مبروك! أنت مؤهل للحصول على الشهادة**
• يمكنك أن تغيب {result['remaining_can_miss']} يوم إضافي دون فقدان الأهلية"""
                else:
                    response += f"""❌ **للأسف، لست مؤهل حالياً للحصول على الشهادة**
• تجاوزت الحد المسموح بـ {result['over_by']} يوم
• تحتاج إلى تحسين حضورك للوصول لنسبة 90%"""

                response += "\n\n💡 **نصيحة:** احرص على الحضور المنتظم لضمان الاستفادة الكاملة والحصول على الشهادة!"
                return response
            else:
                return "لم أتمكن من فهم عدد أيام الغياب. يرجى كتابة الرقم بوضوح\n(مثال: غبت 3 أيام، أو 0 إذا لم تغب)"

    return None

# ================== Enhanced CSS مع الألوان السابقة ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;600;700&display=swap');

/* Hide Streamlit default elements */
#MainMenu, footer, header {visibility: hidden;}
.stAppDeployButton, .stDecoration {display: none;}

/* Global font */
* { font-family: 'Tajawal', sans-serif !important; }

/* Page background - نفس الألوان السابقة */
.stApp {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

/* Intro page styling */
.intro-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: auto;
    padding: 0.5rem;
    margin-top: 0rem;
}
.intro-hero {
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    padding: 2rem 1.5rem;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    max-width: 600px;
    width: 100%;
}
.hero-badge {
    background: rgba(0, 247, 255, 0.2);
    color: #00F7FF;
    padding: 0.5rem 1.5rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 2rem;
    border: 1px solid rgba(0, 247, 255, 0.3);
    display: inline-block;
}
.hero-icon { 
    font-size: 5rem; 
    margin: 1rem 0 2rem 0; 
    animation: float 3s ease-in-out infinite; 
}
@keyframes float { 
    0%, 100% { transform: translateY(0px);} 
    50% { transform: translateY(-10px);} 
}
.hero-title { 
    color: white; 
    font-size: 3.2rem; 
    font-weight: 700; 
    margin: 0 0 1rem 0; 
    text-shadow: 0 2px 15px rgba(0,0,0,.3); 
    line-height: 1.2; 
}
.hero-subtitle { 
    color: rgba(255,255,255,.9); 
    font-size: 1.3rem; 
    text-shadow: 0 1px 8px rgba(0,0,0,.2); 
    line-height: 1.6; 
    margin-bottom: 2rem;
}

/* Quick Actions في شاشة الترحيب - REMOVED */

/* Enhanced Chat Container */
.enhanced-chat-container {
    max-width: 1200px;
    margin: 0 auto;
    height: 95vh;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    position: relative;
}

/* Enhanced Chat Header */
.enhanced-chat-header {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    padding: 1.5rem 2rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.15);
    display: flex;
    align-items: center;
    gap: 1.2rem;
    position: relative;
    overflow: hidden;
}

.enhanced-chat-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
    pointer-events: none;
}

.enhanced-avatar {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea, #764ba2);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    color: white;
    border: 3px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    position: relative;
    z-index: 1;
}

.enhanced-chat-info {
    flex: 1;
    position: relative;
    z-index: 1;
}

.enhanced-chat-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: white;
    margin: 0 0 0.3rem 0;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.enhanced-chat-status {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin: 0;
}

.status-indicator {
    width: 8px;
    height: 8px;
    background: #00ff88;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.7; transform: scale(1.1); }
}

/* Enhanced Messages Area */
.enhanced-messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.05);
    position: relative;
}

.enhanced-messages-container::-webkit-scrollbar {
    width: 6px;
}

.enhanced-messages-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 10px;
}

.enhanced-messages-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.3);
    border-radius: 10px;
}

.enhanced-messages-container::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.5);
}

/* Enhanced Welcome State */
.enhanced-welcome {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 3rem 2rem;
    height: 100%;
    position: relative;
}

.enhanced-welcome::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.enhanced-welcome-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.9;
    animation: float 3s ease-in-out infinite;
    position: relative;
    z-index: 1;
}

.enhanced-welcome-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin-bottom: 0.8rem;
    text-shadow: 0 2px 15px rgba(0, 0, 0, 0.3);
    position: relative;
    z-index: 1;
}

.enhanced-welcome-subtitle {
    font-size: 1rem;
    color: rgba(255, 255, 255, 0.9);
    line-height: 1.7;
    margin-bottom: 2rem;
    max-width: 500px;
    text-shadow: 0 1px 8px rgba(0, 0, 0, 0.2);
    position: relative;
    z-index: 1;
}

.enhanced-quick-actions {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 600px;
}

.enhanced-quick-title {
    color: white;
    font-weight: 700;
    margin: 0 0 1.5rem 0;
    font-size: 1.1rem;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

/* Enhanced Message Bubbles */
.enhanced-message {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    animation: slideInMessage 0.4s ease-out;
    position: relative;
}

@keyframes slideInMessage {
    from {
        opacity: 0;
        transform: translateY(20px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.enhanced-message.user-msg {
    flex-direction: row-reverse;
    text-align: right;
}

.enhanced-msg-avatar {
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    font-weight: 600;
    flex-shrink: 0;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.user-msg .enhanced-msg-avatar {
    background: linear-gradient(135deg, #6A0DAD, #8B38F7);
    color: #fff;
}

.bot-msg .enhanced-msg-avatar {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: #fff;
}

.enhanced-msg-bubble {
    max-width: 75%;
    padding: 1rem 1.3rem;
    border-radius: 20px;
    font-size: 0.9rem;
    line-height: 1.7;
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    word-wrap: break-word;
    position: relative;
    backdrop-filter: blur(10px);
}

.user-msg .enhanced-msg-bubble {
    background: linear-gradient(135deg, #6A0DAD, #8B38F7);
    color: #fff;
    border-bottom-right-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.bot-msg .enhanced-msg-bubble {
    background: rgba(255, 255, 255, 0.95);
    color: #333;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-bottom-left-radius: 8px;
}

/* Enhanced Input Area */
.enhanced-input-container {
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    border-top: 1px solid rgba(255, 255, 255, 0.15);
    position: relative;
}

.enhanced-input-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
    pointer-events: none;
}

.enhanced-input-form {
    position: relative;
    z-index: 1;
}

/* Enhanced Input Styling */
.stTextInput > div > div > input {
    border: 2px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 25px !important;
    padding: 1rem 1.3rem !important;
    font-size: 0.9rem !important;
    background: rgba(255, 255, 255, 0.95) !important;
    color: #333333 !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1) !important;
}

.stTextInput > div > div > input:focus {
    border-color: rgba(102, 126, 234, 0.6) !important;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2) !important;
    transform: translateY(-1px) !important;
}

.stTextInput > div > div > input::placeholder {
    color: #999999 !important;
    opacity: 1 !important;
}

.stTextInput > label {
    display: none !important;
}

/* Enhanced Buttons */
.stButton > button {
    background: rgba(0, 247, 255, 0.2) !important;
    color: #00F7FF !important;
    border: 1px solid rgba(0, 247, 255, 0.3) !important;
    border-radius: 22px !important;
    padding: 0.7rem 1.2rem !important;
    font-size: 0.75rem !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    font-weight: 600 !important;
    margin-bottom: 0.5rem !important;
    width: 100% !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: 0 4px 15px rgba(0, 247, 255, 0.1) !important;
}

.stButton > button:hover {
    background: rgba(0, 247, 255, 0.3) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0, 247, 255, 0.3) !important;
}

/* Enhanced Start Button */
div[data-testid="stButton"] > button[key="start_chat"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 1.2rem 3rem !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    transition: all 0.4s ease !important;
    cursor: pointer !important;
    box-shadow: 0 12px 35px rgba(102, 126, 234, 0.4) !important;
    width: auto !important;
    margin: 0 auto !important;
    display: block !important;
    position: relative !important;
    overflow: hidden !important;
}

div[data-testid="stButton"] > button[key="start_chat"]::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: left 0.5s ease;
}

div[data-testid="stButton"] > button[key="start_chat"]:hover::before {
    left: 100%;
}

div[data-testid="stButton"] > button[key="start_chat"]:hover {
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 20px 50px rgba(102, 126, 234, 0.5) !important;
}

/* Enhanced Form Submit Button */
.stForm > div > div > button[kind="formSubmit"] {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 22px !important;
    padding: 0.7rem 1.3rem !important;
    font-size: 0.9rem !important;
    transition: all 0.3s ease !important;
    cursor: pointer !important;
    font-weight: 600 !important;
    width: 100% !important;
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2) !important;
}

.stForm > div > div > button[kind="formSubmit"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(102, 126, 234, 0.3) !important;
}

/* Enhanced Reset Button */
.reset-btn {
    background: rgba(255, 86, 86, 0.15) !important;
    color: #ff5656 !important;
    border: 1px solid rgba(255, 86, 86, 0.3) !important;
    border-radius: 22px !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.85rem !important;
    margin-bottom: 0.8rem !important;
    width: auto !important;
    backdrop-filter: blur(10px) !important;
}

.reset-btn:hover {
    background: rgba(255, 86, 86, 0.25) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 5px 20px rgba(255, 86, 86, 0.2) !important;
}

/* Enhanced Chat Image */
.enhanced-chat-image {
    max-width: 100%;
    border-radius: 15px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.2);
    margin: 0.5rem 0;
    transition: transform 0.3s ease;
}

.enhanced-chat-image:hover {
    transform: scale(1.02);
}

/* Enhanced Attention Mode Indicator */
.enhanced-attention-indicator {
    background: rgba(0, 247, 255, 0.15);
    border: 1px solid rgba(0, 247, 255, 0.3);
    border-radius: 15px;
    padding: 1rem;
    margin: 1rem 0;
    color: #00F7FF;
    font-weight: 600;
    text-align: center;
    backdrop-filter: blur(10px);
    box-shadow: 0 5px 20px rgba(0, 247, 255, 0.1);
}

/* Responsive Design */
@media (max-width: 1024px) {
    .intro-hero {
        padding: 2.5rem 1.5rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-icon {
        font-size: 4rem;
    }
    
    .enhanced-chat-container {
        height: auto;
        min-height: 80vh;
        margin: 0.5rem;
        border-radius: 25px;
    }
    
    .enhanced-chat-header {
        padding: 1.2rem 1.5rem;
    }
    
    .enhanced-avatar {
        width: 45px;
        height: 45px;
        font-size: 1.3rem;
    }
    
    .enhanced-messages-container {
        padding: 1rem;
    }
    
    .enhanced-msg-bubble {
        max-width: 85%;
        padding: 0.9rem 1.1rem;
        font-size: 0.85rem;
    }
}

@media (max-width: 768px) {
    .enhanced-welcome {
        padding: 2rem 1rem;
    }
    
    .enhanced-welcome-icon {
        font-size: 3rem;
    }
    
    .enhanced-welcome-title {
        font-size: 1.3rem;
    }
    
    .enhanced-welcome-subtitle {
        font-size: 0.9rem;
    }
    
    .enhanced-input-container {
        padding: 1rem;
    }
    
    .enhanced-msg-bubble {
        max-width: 90%;
        padding: 0.8rem 1rem;
        font-size: 0.8rem;
    }
}
</style>
""", unsafe_allow_html=True)

# ================== QA Dictionary ==================
qa_dict = {
    "التحية": {"patterns":[r"\b(مرحبا|أهلا|هلا|سلام|السلام عليكم|صباح الخير|مساء الخير)\b"], "responses":["أهلاً وسهلاً! كيف أقدر أساعدك اليوم؟"]},
    "الوداع": {"patterns":[r"\b(مع السلامة|وداعاً|باي|شكرا لك|في حفظ الله|في أمان الله|أراك لاحقاً)\b"], "responses":["حياك الله! إذا احتجت أي شيء، أنا هنا للمساعدة."]},
    "المساعدة": {"patterns":[r"\b(مساعدة|المساعدة|كيف تقدر تساعدني|تساعدني|وش ممكن أسوي|كيف أقدر أساعد|ممكن مساعدة|أحتاج مساعدة|دعم|ساعدني)\b"], "responses":[
        "أنا هنا للمساعدة! تقدر تسألني عن أي شيء يخص أكاديمية طويق, مثل انك تسألني عن طويق نفسها وإنجازاتها وأهدافها, الخدمات اللي تقدمها الأكاديمية, المعسكرات والبرامج, الشهادات وشروط الحصول عليها, واجبات ومسؤوليات المتدرب, كيف ترفع أعذار الغياب, التدريب التعاوني, أو حتى خريطة الأكاديمية ومرافقها وأماكن القاعات! وكذلك ممكن تستفسر من خلال البريد الإلكتروني التالي: tuwaiqacademy@tuwaiq.edu.sa",
        "كما يمكنني مساعدتك في **حساب أهلية الحصول على الشهادة** بناءً على نسبة الحضور 90%. فقط اكتب 'حساب الشهادة' أو 'حساب حضور' وسأساعدك!"
    ]},
    "طويق": {"patterns":[r"\b(طويق|أكاديمية طويق|مركز طويق|معهد طويق)\b"], "responses":["أكاديمية طويق جهة تعليمية سعودية متخصصة في المهارات التقنية المتقدمة، تقدم معسكرات وبرامج تدريبية في مجالات مثل الذكاء الاصطناعي، الأمن السيبراني، تطوير البرمجيات، وتحليل البيانات. تهدف الأكاديمية إلى تأهيل الكفاءات الوطنية في مجالات التقنية المتقدمة بهدف سد الفجوة بين التعليم واحتياجات سوق العمل من خلال تدريب عملي مكثّف وشراكات مع كبرى الشركات العالمية."]},
    "الإنجازات": {"patterns":[r"\b(الانجازات|انجازاتكم|وش انجازاتكم|انجازات|انجاز|وش حققتوا|إنجازات الاكاديمية|انجازات طويق|الإنجازات|إنجازاتكم|وش إنجازاتكم|وش حققتوا|إنجازات الأكاديمية|إنجازات|إنجاز|إنجازات طويق)\b"], "responses":["""أكاديمية طويق تُعد من أبرز الجهات في المملكة لتأهيل الكفاءات التقنية، حيث درّبت أكثر من 100,000 متدرب ومتدربة عبر برامج ومعسكرات متخصصة في الذكاء الاصطناعي،
         الأمن السيبراني، تطوير البرمجيات، وتحليل البيانات، ونجحت في تنفيذ أكثر من 600 برنامج تدريبي حتى الآن. من أبرز إنجازاتها تنظيم أكبر هاكاثون في العالم 
         "طويق 1000"، إلى جانب شراكاتها مع شركات عالمية مثل Apple وGoogle وMicrosoft وAWS، كما أنشأت أول أكاديمية Apple للمطورين في الشرق الأوسط وأول أكاديمية نسائية من نوعها عالميًا،
         مما جعلها في طليعة مبادرات بناء القدرات التقنية في السعودية."""]},
    "الخدمات": {"patterns":[r"\b(الخدمات|خدمات|وش تقدمون|وش توفرون|وش عندكم|وش تسوون|الخدمة المتاحة|وش أقدر أستفيد|الخدمة المقدمة|ايش عندكم|المجالات)\b"], "responses":["نقدم خدمات متنوعة تشمل برامج تدريبية، معسكرات تقنية، وشهادات معتمدة لفئات مختلفة مثل الكبار والناشئين. تفضل اسأل عن النوع أو الفئة اللي تهمك."]},
    "الكبار": {"patterns":[r"\b(كبار|بالغين|كبار السن|فوق 18|راشدين|طلاب الجامعة|جامعيين|متقدمين|فئة الكبار|أعمار كبيرة|فئة البالغين|مرحلة جامعية)\b"], "responses":["لفئة الكبار، الأكاديمية تقدم برامج متقدمة، معسكرات مكثفة، وشهادات احترافية تغطي مجالات التقنية الحديثة."]},
    "الناشئين": {"patterns":[r"\b(ناشئين|صغار|أطفال|أقل من 18|مراهقين|طلاب ابتدائي|طلاب متوسط|المرحلة المتوسطة|صغار السن|فئة الناشئين|الناشئين)\b"], "responses":["للناشئين، عندنا برامج تفاعلية، ومعسكرات ممتعة تناسب أعمارهم وتساعدهم في بداية مشوارهم التقني."]},
    "المعسكرات": {"patterns":[r"\b(معسكر|معسكرات|المعسكرات|bootcamp|معسكر تدريبي|دورة مكثفة|وش المعسكرات|التسجيل في معسكر|برنامج مكثف|برنامج تدريبي مكثف)\b"], "responses":["تقدم الأكاديمية مجموعة متنوعة من المعسكرات في المجالات التقنية الحديثة والمطلوبة في سوق العمل, تقدر تشوف قائمة المعسكرات المتاحة حالياً والتسجيل فيها من خلال الرابط في أعلى الصفحة."]},
    "الشهادات": {"patterns":[r"\b(شهادة|شهادات|أبغى شهادة|تبون شهادة|هل في شهادة|هل تعطون شهادات|توثيق|معترف فيها|شهادة موثقة|معتمدة|الشهادات)\b"], "responses":[""" أغلب المعسكرات والبرامج تقدم شهادات معتمدة من الأكاديمية بعد اجتياز متطلباتها, والي هي:
         1- الحصول على نسبة 80% في التقييم النهائي
         2- حضور 90% من المحاضرات
         3- إتمام المشاريع المطلوبة بالوقت المحدد واستيفاء معايير الجودة
         4- إتمام التدريب التعاوني بعد الانتهاء من فترة المعسكر ويتم تقسيم الدرجة النهائية من 100 كالتالي:
         10% للتفاعل والمشاركة, 20% للتمارين والمهام اليومية, 10% للإختبارات, 30% للمشاريع, و 30% للمشروع النهائي.
         
         💡 **يمكنني مساعدتك في حساب أهلية الحصول على الشهادة بناءً على نسبة الحضور!** فقط اكتب 'حساب الشهادة' أو 'حساب حضور'."""]},
    "البرامج": {"patterns":[r"\b(برنامج|برامج|كورسات|الدورات|كورس|التدريب|وش البرامج|وش الدورات|المناهج|برامج تدريبية|وش أقدر أتعلم)\b"], "responses":["تقدم الاكاديمية برامج متنوعة في مجالات محتلفة, في منها الحضوري والي عن بعد, تقدر تتصفح كل البرامج والدورات اللي تقدمها الأكاديمية حالياً عن طريق الرابط في أعلى الصفحة"]},
    "التسجيل": {"patterns":[r"\b(التسجيل|أسجل|كيف أسجل|أبغى أسجل|عملية التسجيل|ادخل|أدخل|التسجيل في معسكر|التسجيل في دورة)\b"], "responses":["يمكنك التسجيل في البرامج والمعسكرات من خلال الرابط في أعلى الصفحة, إذا احتجت مساعدة في عملية التسجيل أنا هنا للمساعدة!"]},
    "واجبات_ومسؤوليات_المتدرب": {"patterns":[r"\b(واجبات|مسؤوليات|المهام|الالتزامات)\b"], "responses":["""يلتزم المتدرب بتوقيع عقد التدريب في مقر أكاديمية طويق قبل بدء المعسكر أو البرنامج، والحفاظ على الذوق العام وارتداء الملابس الرسمية داخل المبنى،
         مع الالتزام بتعليمات إدارة الأمن والسلامة عند الدخول والخروج. يجب عدم تناول الأطعمة في القاعات التدريبية، ويُمنع التدخين داخل المبنى،
         كما يلزم إحضار جهاز كمبيوتر بالمواصفات المطلوبة طوال فترة البرنامج والمشاركة في تنفيذ المشاريع العملية ضمن المدة المحددة لتحقيق الفائدة المعرفية. 
         على المتدرب تعبئة الاستبيانات المطلوبة بدقة ووضوح للمساهمة في تطوير التدريب، والحضور الكامل طوال فترة البرنامج كشرط لاستلام الشهادة.
         في حال التغيب، يجب إرسال العذر الطبي إلى إدارة الشؤون الأكاديمية عبر البريد الإلكتروني المخصص، مع الالتزام بأوقات الحضور والانصراف وعدم البقاء في القاعات بعد انتهاء الدوام التدريبي.
         الأكاديمية غير مسؤولة عن فقدان الأغراض الشخصية، ويحق لموظفيها التقاط الصور وتسجيل الفيديوهات واستخدامها للأغراض الإعلانية أو التوثيقية دون الحاجة إلى موافقات مسبقة.
         """]},
    "الغياب": {"patterns":[r"\b(غياب|تغيب|عذر غياب|أعذار|أعذار غياب|اعذار|اعذار غياب|غبت|غايب|غائب|عذر)\b"], "responses":["""لرفع عذر الغياب، يبدأ الطالب بتسجيل الدخول إلى منصة أكاديمية طويق باستخدام اسم المستخدم وكلمة المرور،
         ثم الانتقال إلى قسم "السجل الأكاديمي" من القائمة الرئيسية والوصول إلى خدمة رفع أعذار الغياب.
         بعد ذلك يقوم بتحديد سبب الغياب من الخيارات المتاحة وإرفاق المستندات المطلوبة،
         ثم مراجعة صحة البيانات والتأكد منها قبل الضغط على "إرسال". يمكن للطالب متابعة حالة الطلب لمعرفة إذا كان مقبولًا أو مرفوضًا من خلال النقر على زر المتابعة في خانة الحالات 
         """]},
    "الأسئلة_الشائعة": {"patterns":[r"\b(أسئلة شائعة|الأسئلة المتكررة|استفسارات|استفسار)\b"], "responses":["تفضل، أنا هنا للإجابة على أسئلتك!"]},
    "التدريب_التعاوني": {"patterns":[r"\b(التدريب التعاوني|التدريب|التدريب العملي|التدريب الميداني|التدريب في الشركات|التدريب الخارجي)\b"], "responses":["""يعد اكمال التدريب التعاوني شرطاً أساسياً للحصول على شهادة اجتياز المعسكرات, حيث يهدف البرنامج إلى تزويدك بالمهارات والمعرفة العملية اللازمة لسوق العمل في أهم مجالات التقنية الحديثة, 
        ويطلب منك رفع ما يثبت بدء المتدرب لمرحلة التدريب التعاوني خلال ثلاث أشهر بعد انتهاء المعسكر بحد أقصى, 
        وهناك استثناءات في حال كنت موظف, أو طالب جامعي ولديك تدريب تعاوني للجامعة, أو إذا حصلت على عرض وظيفي مؤكد."""]},
    "الخريطة": {"patterns":[
            r"\b(الخريطة|خريطة المكان|خريطة الأكاديمية|وين موقعكم|رسم توضيحي|خريطة طويق|وين القاعات|ارسلها|أرسلها|أرسل|ارسل|ايه|ياليت|هات|هاتها|اي|أماكن القاعات|وين الفصول|وين قاعة|مكان قاعة|قاعة|كلاس|غرفة|أين قاعة|كيف أروح قاعة)\b"
        ], "responses":[{"text":"تفضل هذه خريطة الأكاديمية توضح المرافق وأماكن القاعات:","image": str(logo_path) if logo_path else ""}]},
    "المرافق": {"patterns":[
            r"\b(دورات المياه|الحمام|الحمامات|مغاسل|مصلى|أصلي|اصلي|ما صليت|صلاة|صلاه|مكان الوضوء)\b",
            r"\b(كوفي|كافيه|قهوتكم|مقاهي|المقاهى|المقهى|مقهى|كافيهات|قهوة)\b",
            r"\b(مطعم|الأكل|فيه أكل|مكان الغدا|الاكل|اكل|آكل|ما اكلت|ما أكلت|جوعان|ما تغديت|مطاعم|المطاعم|المطعم|بوفيه|كافتيريا)\b"
        ], "responses":["بالنسبة للمرافق العامة: دورات المياه موجودة بجانب القاعات وبتلاقيها موزعة في جميع الممرات تقريباً, وفيه مصلى للرجال والنساء في الدور الأول, فيه دانكن دونتس موجود بجانب المدخل الرئيسي. فيه مطعم صب واي بعد, تقدر تشوف المرافق بالخريطة وإذا مو ظاهرة لك ممكن أرسلها لك."]},
    "الخصومات": {"patterns":[r"\b(خصم|خصومات|كوبونات|اجار|أجار|استاجر|استأجر|سكن|سيارة|سيارات|مواصلات|مركبة|مركبات|تخفيض|تخفيضات|عروض|عرض)\b"], "responses":[
        "أكاديمية طويق تقدم لطلابها مجموعة من الخصومات والعروض الخاصة على الفنادق والشقق المفروشة وكذلك مكاتب تأجير السيارات، إذا قدمت وانقبلت سواء في معسكر أو برنامج بتجيك رسالة على الإيميل وفيها قائمة من كوبونات الخصم اللي تتحدث باستمرار."
    ]}
}

#  Router 
def get_response(user_input):
    # 1) Attendance flow has priority
    attendance_response = handle_attendance_flow(user_input)
    if attendance_response:
        return attendance_response

    # 2) Regular patterns
    for category, qa in qa_dict.items():
        for pattern in qa["patterns"]:
            if re.search(pattern, user_input, re.IGNORECASE):
                return random.choice(qa["responses"])
    return "ما فهمت عليك، تقدر توضح أكثر أو تسأل بشكل مختلف؟"

#  MAIN UI 
if not st.session_state.show_chat:
    #  Intro page بدون الأسئلة السريعة
    st.markdown("""
    <div class="intro-container">
        <div class="intro-hero">
            <div class="hero-badge">محدث أغسطس 2025</div>
            <div class="hero-icon">🤖</div>
            <h1 class="hero-title">أنا مساعد ! ولي من اسمي نصيب</h1>
            <p class="hero-subtitle">مساعدك الشخصي للاستفسار عن المعسكرات والبرامج والخدمات المقدمة</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Start button only
    if st.button("🚀 ابدأ المحادثة", key="start_chat", help="ابدأ المحادثة مع المساعد الذكي"):
        st.session_state.show_chat = True
        st.rerun()

    #  إظهار تفعيل وضع الحاسبة لو كان شغال قبل الدخول
    if st.session_state.attn_mode:
        st.markdown('<div class="enhanced-attention-indicator">📊 **وضع حساب الشهادة نشط** - ' + str(st.session_state.attn_awaiting) + '</div>', unsafe_allow_html=True)

    st.markdown("""
        </div>
    </div>
    """, unsafe_allow_html=True)

else:

    # Enhanced Header
    st.markdown("""
    <div class="enhanced-chat-header">
        <div class="enhanced-avatar">🤖</div>
        <div class="enhanced-chat-info">
            <h3 class="enhanced-chat-title">مساعد طويق</h3>
            <p class="enhanced-chat-status">
                <span class="status-indicator"></span>
                متصل الآن • جاهز للمساعدة
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Enhanced Messages container
    st.markdown('<div class="enhanced-messages-container">', unsafe_allow_html=True)

    if len(st.session_state.history) == 0:
        # Enhanced welcome section
        st.markdown("""
        <div class="enhanced-welcome">
            <div class="enhanced-welcome-icon">💬</div>
            <div class="enhanced-welcome-title">أهلاً وسهلاً بك!</div>
            <div class="enhanced-welcome-subtitle">
                أنا مساعد أكاديمية طويق الذكي، جاهز للإجابة على جميع استفساراتك حول المعسكرات،
                البرامج، الشهادات، والخدمات المقدمة
            </div>
            <div class="enhanced-quick-actions">
                <div class="enhanced-quick-title">أسئلة سريعة:</div>
        </div>
        """, unsafe_allow_html=True)

        # Quick buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("ما هي أكاديمية طويق؟", key="quick1_chat"):
                st.session_state.history.append(("user", "ما هي أكاديمية طويق؟", now_str()))
                response = get_response("ما هي أكاديمية طويق؟")
                st.session_state.history.append(("bot", response, now_str()))
                st.rerun()

            if st.button("شروط الشهادات", key="quick3_chat"):
                st.session_state.history.append(("user", "شروط الشهادات", now_str()))
                response = get_response("شروط الشهادات")
                st.session_state.history.append(("bot", response, now_str()))
                st.rerun()

        with col2:
            if st.button("المعسكرات المتاحة", key="quick2_chat"):
                st.session_state.history.append(("user", "المعسكرات المتاحة", now_str()))
                response = get_response("المعسكرات المتاحة")
                st.session_state.history.append(("bot", response, now_str()))
                st.rerun()

            if st.button("خريطة الأكاديمية", key="quick4_chat"):
                st.session_state.history.append(("user", "خريطة الأكاديمية", now_str()))
                response = get_response("خريطة الأكاديمية")
                if isinstance(response, dict):
                    st.session_state.history.append(("bot", response["text"], now_str()))
                    st.session_state.history.append(("image", response["image"], now_str()))
                else:
                    st.session_state.history.append(("bot", response, now_str()))
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)  # Close enhanced-quick-actions

        # Attendance mode indicator 
        if st.session_state.attn_mode:
            st.markdown('<div class="enhanced-attention-indicator">📊 **وضع حساب الشهادة نشط** - ' + str(st.session_state.attn_awaiting) + '</div>', unsafe_allow_html=True)

        # Enhanced welcome input area
        st.markdown('<div class="enhanced-input-container">', unsafe_allow_html=True)
        st.markdown('<div class="enhanced-input-form">', unsafe_allow_html=True)
        with st.form(key="welcome_form", clear_on_submit=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                user_input = st.text_input(
                    "message",
                    placeholder="اكتب رسالتك هنا واضغط Enter أو زر الإرسال...",
                    label_visibility="collapsed",
                    key="user_message_welcome"
                )
            with c2:
                send_clicked = st.form_submit_button("📤 إرسال")
        st.markdown('</div>', unsafe_allow_html=True)  # Close enhanced-input-form
        st.markdown('</div>', unsafe_allow_html=True)  # Close enhanced-input-container

        # Handle message sending from welcome
        if send_clicked and user_input.strip():
            st.session_state.history.append(("user", user_input, now_str()))
            response = get_response(user_input)
            if isinstance(response, dict) and "image" in response:
                st.session_state.history.append(("bot", response["text"], now_str()))
                st.session_state.history.append(("image", response["image"], now_str()))
            else:
                st.session_state.history.append(("bot", response, now_str()))
            st.rerun()

    else:
        # Show enhanced conversation history
        for entry in st.session_state.history:
            # دعم كلا الشكلين: 2 أو 3 عناصر في tuple
            if len(entry) == 3:
                sender, message, ts = entry
            else:
                sender, message = entry
                ts = now_str()

            if sender == "image":
                b64 = img_to_base64(message) or ""
                st.markdown(f"""
                <div class="enhanced-message bot-msg">
                    <div class="enhanced-msg-avatar">🗺️</div>
                    <div class="enhanced-msg-bubble">
                        <img src="data:image/png;base64,{b64}" class="enhanced-chat-image" alt="خريطة الأكاديمية">
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif sender == "user":
                st.markdown(f"""
                <div class="enhanced-message user-msg">
                    <div class="enhanced-msg-avatar">👤</div>
                    <div class="enhanced-msg-bubble">{message}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="enhanced-message bot-msg">
                    <div class="enhanced-msg-avatar">🤖</div>
                    <div class="enhanced-msg-bubble">{message}</div>
                </div>
                """, unsafe_allow_html=True)

        # Attendance mode indicator during chat
        if st.session_state.attn_mode:
            st.markdown('<div class="enhanced-attention-indicator">📊 **وضع حساب الشهادة نشط** - ' + str(st.session_state.attn_awaiting) + '</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close enhanced-messages-container

    #  Enhanced Input Area for ongoing chat 
    if len(st.session_state.history) > 0:
        st.markdown('<div class="enhanced-input-container">', unsafe_allow_html=True)
        st.markdown('<div class="enhanced-input-form">', unsafe_allow_html=True)
        with st.form(key="chat_form", clear_on_submit=True):
            c1, c2 = st.columns([4, 1])
            with c1:
                user_input_chat = st.text_input(
                    "message_chat",
                    placeholder="اكتب رسالتك هنا واضغط Enter أو زر الإرسال...",
                    label_visibility="collapsed",
                    key="user_message_chat"
                )
            with c2:
                send_clicked_chat = st.form_submit_button("📤 إرسال")
        st.markdown('</div>', unsafe_allow_html=True)  # Close enhanced-input-form
        st.markdown('</div>', unsafe_allow_html=True)  # Close enhanced-input-container

        # Handle message sending from chat
        if send_clicked_chat and user_input_chat.strip():
            st.session_state.history.append(("user", user_input_chat, now_str()))
            response = get_response(user_input_chat)
            if isinstance(response, dict) and "image" in response:
                st.session_state.history.append(("bot", response["text"], now_str()))
                st.session_state.history.append(("image", response["image"], now_str()))
            else:
                st.session_state.history.append(("bot", response, now_str()))
            st.rerun()

    # Enhanced Back to intro button (reset everything)
    if st.button("🏠 العودة للصفحة الرئيسية", key="back_to_intro"):
        st.session_state.show_chat = False
        st.session_state.history = []
        st.session_state.last_input = ""
        # تصفير متغيرات الحاسبة
        st.session_state.attn_mode = False
        st.session_state.attn_absences = None
        st.session_state.attn_total_days = None
        st.session_state.attn_awaiting = None
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # close enhanced-chat-container
    