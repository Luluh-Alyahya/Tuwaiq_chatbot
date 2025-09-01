import streamlit as st
import streamlit.components.v1 as components
import base64, os, datetime, random


st.set_page_config(page_title="أكاديمية طويق 🎓", layout="wide", page_icon="🏛️")

def img_to_base64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""


hero_path = os.path.join(os.path.dirname(__file__), "images", "hero.jpg")
hero_b64  = img_to_base64(hero_path)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;600;700&display=swap');
#MainMenu, footer, header, .stAppDeployButton, .stDecoration {{ display:none; }}
* {{ font-family:'Tajawal',sans-serif !important; }}

.stApp {{
  background: linear-gradient(135deg,#EBF1FF 0%,#F7F3FF 100%);
  min-height: 100vh;
}}

.main .block-container {{
  padding: 1rem !important;
  max-width: 1200px !important;
}}

.overlay-content {{ position: relative; z-index: 1; }}

/* ========== بانر الهيدر فقط ========== */
.page-hero {{
  position: relative; border-radius: 24px; overflow: hidden; height: 220px;
  margin: 10px 0 20px 0;
  background: url('data:image/jpeg;base64,{hero_b64}') center/cover no-repeat;
}}
.page-hero::after {{ content:''; position:absolute; inset:0;
  background: linear-gradient(180deg, rgba(0,0,0,.25), rgba(0,0,0,.25)); }}
.hero-inner {{ position:relative; z-index:1; height:100%;
  display:flex; align-items:center; justify-content:flex-end; padding: 0 24px; text-align:right; color:#fff; }}
.hero-title {{ font-size: 36px; font-weight: 800; margin:0; }}
.hero-sub   {{ font-size: 18px; opacity:.95; margin-top:8px; }}

/* محتوى الصفحة الأبيض */
.main-content {{
  background: #ffffff; border-radius: 24px; padding: 32px;
  border: 1px solid #EEF0F6; box-shadow: 0 8px 30px rgba(20, 20, 43, 0.06);
  margin-bottom: 18px;
}}
.big-title {{ font-size: 32px; font-weight: 800; color: #5d23b3; margin-bottom: 6px; }}
.subheading {{ font-size: 18px; color: #6B7280; margin-bottom: 24px; }}
.stat-box {{
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 18px; padding: 20px 14px; text-align: center;
  border: 1px solid #EDF0FF; box-shadow: 0 8px 24px rgba(0,0,0,.06);
  transition: transform .2s ease; margin-bottom: 16px;
}}
.stat-box:hover {{ transform: translateY(-4px); }}
.stat-number {{ font-size: 28px; font-weight: 800; color: #005BA5; margin-bottom: 6px; }}
.stat-label  {{ font-size: 14px; color: #666; font-weight: 600; }}
.program-description {{
  background: #fff; border-radius: 16px; padding: 20px; border: 1px solid #EEE;
  text-align: right; line-height: 1.8; font-size: 16px; color: #4a4a4a;
}}
.white-button {{
  background:#ffffff !important; color:#333 !important; font-size:16px !important; font-weight:700 !important;
  padding:10px 22px !important; border-radius:22px !important; text-decoration:none !important;
  display:inline-block !important; transition:transform .2s, box-shadow .2s !important;
  box-shadow:0 6px 18px rgba(0,0,0,.12) !important; border:1px solid #E6E6E6 !important;
}}
.white-button:hover {{ transform: translateY(-2px) !important; box-shadow:0 12px 28px rgba(0,0,0,.16) !important; }}

/* chat*/
.chatbot-hero {{
  background: linear-gradient(145deg, rgba(255,255,255,.98) 0%, rgba(248,250,255,.98) 100%);
  border-radius: 24px; padding: 32px 24px; border: 1px solid #EEF0FF;
  box-shadow: 0 12px 34px rgba(0,0,0,.06); position: relative; overflow: hidden; direction: rtl; margin-top: 12px;
}}
.chatbot-container {{ display:flex; align-items:center; gap: 28px; }}
.chatbot-avatar {{
  width: 120px; height:120px; border-radius:50%; background: linear-gradient(145deg, #667eea, #764ba2);
  color:#fff; display:flex; align-items:center; justify-content:center; font-size:58px;
  border:4px solid #fff; box-shadow: 0 10px 24px rgba(102,126,234,.3);
}}
.chatbot-info {{ flex:1; text-align:right; }}
.chatbot-greeting {{
  font-size: 28px; font-weight:800; background: linear-gradient(135deg, #667eea, #764ba2);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:8px;
}}
.chatbot-description {{ font-size:18px; color:#6B7280; margin-bottom:18px; font-weight:500; }}
.chatbot-features {{ display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; margin-bottom:18px; }}
.feature-tag {{ background: rgba(102,126,234,.1); color:#667eea; padding:6px 12px; border-radius:16px; font-size:13px; font-weight:700; border:1px solid rgba(102,126,234,.2); }}
.chatbot-buttons {{ display:flex; gap:12px; justify-content:flex-end; flex-wrap:wrap; }}
.chat-btn-primary {{
  background: linear-gradient(135deg, #667eea, #764ba2); color:#fff; font-weight:800; padding:12px 22px;
  border-radius:20px; text-decoration:none; display:inline-flex; gap:8px; border:none;
  box-shadow:0 10px 22px rgba(102,126,234,.28); transition: transform .2s ease;
}}
.chat-btn-primary:hover {{ transform: translateY(-2px); }}
.chat-btn-secondary {{
  background:#fff; color:#667eea; font-weight:700; padding:10px 18px; border-radius:20px;
  text-decoration:none; display:inline-flex; gap:8px; border:1px solid rgba(102,126,234,.25);
}}

/*cards */
.card{{background:#fff;border:1px solid #EEF0FF;border-radius:18px;padding:20px;box-shadow:0 10px 30px rgba(20,20,43,.06);margin:14px 0}}
.card-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}}
.card-title{{font-weight:800;font-size:20px;color:#333;margin:0}}
.tag{{background:rgba(102,126,234,.1);color:#667eea;border:1px solid rgba(102,126,234,.2);padding:6px 10px;border-radius:14px;font-weight:700;font-size:12px}}
.card-body{{color:#666;line-height:1.7;font-size:15px}}
.divider{{height:1px;background:#EEF0F6;margin:16px 0;border-radius:1px}}
.ticket-title{{font-weight:800;font-size:18px;margin-bottom:8px;color:#333}}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="page-hero">
  <div class="hero-inner">
    <div>
      <h1 class="hero-title">أكاديمية طويق</h1>
      <div class="hero-sub">تعلم تقنيات المستقبل في مكان واحد</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# contant of page
st.markdown('<div class="main-content">', unsafe_allow_html=True)

st.markdown('<div class="big-title">إحصائيات</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading">نظرة سريعة على أرقامنا</div>', unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">1,924,725</div>
            <div class="stat-label"> عدد المسجلين حتى الآن </div>
        </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">2,147</div>
            <div class="stat-label">عدد البرامج والمعسكرات</div>
        </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown("""
        <div class="stat-box">
            <div class="stat-number">38,036</div>
            <div class="stat-label">عدد الخريجين</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="program-description">
معسكرات وبرامج احترافية بالشراكة مع كبرى الجهات العالمية؛ لتطوير مهاراتك…
</div>
<div style="text-align:right; margin: 8px 0 6px;">
  <a class="white-button" href="https://tuwaiq.edu.sa/" target="_blank"> ↖ انتقل لأكاديمية طويق</a>
</div>
""", unsafe_allow_html=True)

# components.html


# chatbot
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="card-header">
    <div class="card-title">🤖 مساعد طويق الذكي</div>
</div>
<div class="card-body" dir="rtl">
    مستعد أجاوبك على أي سؤال يخص الأكاديمية والمعسكرات.
</div>
""", unsafe_allow_html=True)

#  لون زر ابدأ المحادثةةةة
st.markdown("""
<style>
a[data-baseweb="button"] {
    background-color: #5d23b3 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.5em 1em !important;
    text-decoration: none !important;
}
a[data-baseweb="button"]:hover {
    background-color: #4a1c8f !important;
}
</style>
""", unsafe_allow_html=True)

st.link_button("🚀 ابدأ المحادثة", "chatbot", use_container_width=True)




st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="ticket-title" dir="rtl">🎫 رفع تذكرة دعم</div>', unsafe_allow_html=True)
st.markdown('<div class="card-body" dir="rtl">ارسل تذكرتك وسيتم الرد خلال 24 ساعة.</div>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

with st.form("support_ticket", clear_on_submit=True):
    ca, cb = st.columns(2)
    with ca:
        name  = st.text_input("الاسم الكامل", placeholder="مثال: لولوه اليحيى")
    with cb:
        email = st.text_input("البريد الإلكتروني", placeholder="example@email.com")
    topic = st.selectbox("الموضوع", ["استفسار تسجيل", "مشاكل منصة", "مواعيد/قبول", "أخرى"])
    msg   = st.text_area("وصف المشكلة/الاستفسار", height=120, placeholder="اكتب التفاصيل هنا…")
    submitted = st.form_submit_button("إرسال التذكرة ✅")

    if submitted:
        now = datetime.datetime.now()
        tid = f"TQ-{now.strftime('%y%m%d')}-{random.randint(1000,9999)}"

        # CSS suscses 
        st.markdown("""
        <style>
        div.stAlert, div[data-testid="stNotification"], div[data-baseweb="notification"] {
            background-color: #d4edda !important;
            color: #155724 !important;
            opacity: 1 !important;
            filter: none !important;
            border-radius: 10px !important;
            border: 1px solid #c3e6cb !important;
        }
        div.stAlert * , div[data-testid="stNotification"] * , div[data-baseweb="notification"] * {
            color: #155724 !important;
            font-weight: 700 !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.success(f"تم رفع التذكرة! رقم التذكرة: {tid}")
        st.caption("احتفظ برقم التذكرة لمتابعتها مع فريق الدعم.")


st.markdown('</div>', unsafe_allow_html=True)


# team members section
st.markdown('<div class="big-title" style="text-align:center;">فريق العمل</div>', unsafe_allow_html=True)
st.markdown('<div class="subheading" style="text-align:center;">طلاب معسكر بناء وتطوير نماذج الذكاء الاصطناعي</div>', unsafe_allow_html=True)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

member1_b64 = img_to_base64(os.path.join(IMAGES_DIR, "member1.png"))
member2_b64 = img_to_base64(os.path.join(IMAGES_DIR, "member2.png"))
member3_b64 = img_to_base64(os.path.join(IMAGES_DIR, "member3.png"))
member4_b64 = img_to_base64(os.path.join(IMAGES_DIR, "member4.png"))


missing = []
for fname, b64 in [
    ("hero.jpg",  hero_b64),
    ("member1.png", member1_b64),
    ("member2.png", member2_b64),
    ("member3.png", member3_b64),
    ("member4.png", member4_b64),
]:
    if not b64:
        missing.append(fname)
if missing:
    st.warning("الصور التالية غير موجودة داخل images أو لا يمكن قراءتها: " + ", ".join(missing))

team_html = f"""
<!DOCTYPE html>
<html dir="rtl">
<head>
<meta charset="utf-8"/>
<style>
.team-wrap {{
 display: flex;
  gap: 20px;
  justify-content: flex-start;   /* نبدأ من اليمين */
  flex-wrap: nowrap;             /* ممنوع يلف لسطر جديد */
  overflow-x: auto;              /* سحب أفقي إذا ما فيه مساحة */
  padding: 10px 6px;
  scroll-snap-type: x mandatory; /* سناب لطيف أثناء السحب () */
}}
.team-card {{
flex: 0 0 230px;               /* عرض ثابت لكل كارد داخل الفليكس */
  background: #fff;
  border: 1px solid #eee;
  border-radius: 20px;
  box-shadow: 0 8px 20px rgba(0,0,0,.08);
  overflow: hidden;
  text-align: center;
  display: flex;
  flex-direction: column;
  scroll-snap-align: start;      /* سناب لكل كارد */
}}

.team-card img {{
  width: 100%;
  height: 200px; /* حجم ثابت */
  object-fit: cover; /* يضبط القص */
  display: block;
}}

.team-info {{
  padding: 15px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}}

.team-name {{
  font-weight: 800;
  font-size: 18px;
  color: #333;
  margin-bottom: 6px;
}}

.team-role {{
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}}

.team-link {{
  display: inline-block;
  width: 36px;
  height: 36px;
  line-height: 36px;
  border-radius: 50%;
  background: #0A66C2;
  color: #fff;
  text-decoration: none;
  font-weight: 800;
  margin-top: auto;
}}

.team-link:hover {{
  background: #004182;
}}
</style>
</head>
<body>
  <div class="team-wrap">
    <div class="team-card">
      <img src="data:image/png;base64,{member1_b64}" alt="عضو الفريق">
      <div class="team-info">
        <div class="team-name">لولوه اليحيى</div>
        <div class="team-role">AI Optimization & Integration - <br>
             UI/UX Designer-</div>
        <a class="team-link" href="https://www.linkedin.com/in/luluh-alyahya-050024284/" target="_blank">in</a>
      </div>
    </div>

    <div class="team-card">
      <img src="data:image/png;base64,{member2_b64}" alt="عضو الفريق">
      <div class="team-info">
        <div class="team-name">سلطان الجربوع</div>
        <div class="team-role">   Chatbot Content Developer- <br>
     Dialogue Flow Designer- </div>
        <a class="team-link" href="https://www.linkedin.com/in/sultanal-jrboa/" target="_blank">in</a>
      </div>
    </div>

    <div class="team-card">
      <img src="data:image/png;base64,{member3_b64}" alt="عضو الفريق">
      <div class="team-info">
        <div class="team-name">منصور الشمران</div>
        <div class="team-role">  Chatbot Content Developer- <br>
    - -------</div>
        <a class="team-link" href="https://www.linkedin.com/in/mansor-alshamran-948b1a27a/" target="_blank">in</a>
      </div>
    </div>

    <div class="team-card">
      <img src="data:image/png;base64,{member4_b64}" alt="عضو الفريق">
      <div class="team-info">
        <div class="team-name">جود الجبرين</div>
        <div class="team-role"> Data Validator- <br>
       AI Knowledge Developer- </div>
        <a class="team-link" href="https://www.linkedin.com/in/joud-bin-jibreen-877b53193/?utm_source=share&utm_campaign=share_via&utm_content=profile&utm_medium=ios_app" target="_blank">in</a>
      </div>
    </div>
  </div>
</body>

</html>
"""

# cards
components.html(team_html, height=520, scrolling=False)