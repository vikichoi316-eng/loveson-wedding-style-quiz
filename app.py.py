import streamlit as st
import os
import base64

# =========================
# 0) Page config (must be first)
# =========================
st.set_page_config(page_title="Wedding Venue Finder", page_icon="💍", layout="centered")

# =========================
# 1) Background image -> base64
# =========================
def img_to_base64(path: str) -> str:
    if not os.path.exists(path):
        st.error(f"❌ 找不到背景圖片：{path}")
        st.stop()
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_PATH = os.path.join(BASE_DIR, "images", "image3.jpg")
bg_base64 = img_to_base64(IMG_PATH)

# =========================
# 2) Styles (CSS ONLY)
# =========================
st.markdown(f"""
<style>
/* ===== 整體背景：黑色濾鏡 + 背景圖 ===== */
.stApp {{
    background-image:
        linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)),
        url("data:image/jpg;base64,{bg_base64}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
}}

/* ===== 標題、文字（白字清楚） ===== */
h1 {{
    color: #FFFFFF;
    text-align: center;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-weight: 800;
    letter-spacing: 1px;
    text-shadow: 0 2px 20px rgba(0,0,0,0.45);
}}
h2, h3, p, .stMarkdown, label {{
    color: rgba(255,255,255,0.92);
}}

/* ✅ 提示框/通知框文字 */
[data-testid="stAlert"] *,
div[data-testid="stNotificationContent"] * {{
    color: rgba(255,255,255,0.95) !important;
}}

/* ===== info box（玻璃感） ===== */
[data-testid="stAlert"] {{
    background: rgba(255,255,255,0.16);
    backdrop-filter: blur(8px);
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.25);
}}

/* ===== 表單卡片（玻璃卡） ===== */
[data-testid="stForm"] {{
    background: rgba(255,255,255,0.18);
    backdrop-filter: blur(10px);
    border-radius: 18px;
    padding: 24px;
    border: 1px solid rgba(255,255,255,0.25);
}}

/* ===== radio 選項字 ===== */
.stRadio > label, div[role="radiogroup"] label {{
    color: rgba(255,255,255,0.92) !important;
    font-size: 17px;
    font-weight: 600;
}}

/* ===== 按鈕 ===== */
.stButton>button {{
    background: linear-gradient(90deg, #8B5A2B, #A67C52);
    color: white;
    border-radius: 22px;
    border: none;
    width: 100%;
    height: 3em;
    font-weight: bold;
}}
.stButton>button:hover {{
    opacity: 0.92;
}}

/* ===== 小字 ===== */
.small {{
    font-size: 14px;
    color: rgba(255,255,255,0.88);
}}

/* ===== 結果卡片（玻璃卡） ===== */
.card {{
  background: rgba(255,255,255,0.16);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.25);
  border-radius: 14px;
  padding: 14px 16px;
  margin-top: 10px;
}}
</style>
""", unsafe_allow_html=True)



# =========================
# 2) Core categories
# =========================
CATS = [
    "海滩婚礼派 (Beach Wedding)",
    "奢华度假村派 (Luxury Resort)",
    "文化传统派 (Cultural Heritage)",
    "自然隐秘派 (Nature Retreat)",
    "现代简约派 (Modern Minimalist)",
    "豪华宴会派 (Luxury Banquet)",
    "特色别墅派 (Unique Villas)",
    "森林童话派 (Forest Fairytale)",
]

def empty_scores():
    return {c: 0 for c in CATS}

def add(scores, points):
    for cat, val in points.items():
        scores[cat] += val

def add_reason(reasons, points, text):
    # attach the same reason to all cats touched by this answer
    for cat in points.keys():
        reasons[cat].append(text)

def top2(scores):
    items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return items[:2], items

def strength_label(diff: int) -> str:
    if diff >= 6:
        return "取向非常明確（你係典型派）"
    elif diff >= 3:
        return "偏好清晰，但同時有混合風格"
    else:
        return "混合型取向（兩種風格都好適合你）"

# =========================
# 3) Result narratives (consultant tone)
# =========================
RESULT_COPY = {
    "海滩婚礼派 (Beach Wedding)": {
        "title": "🌊 海滩婚礼派",
        "desc": "你追求畫面感與情感張力。婚禮對你嚟講係一幕電影——海天一線、光線、風同地平線，缺一不可。",
        "bullets": ["浪漫氛圍", "儀式感與照片張力", "願意為畫面而移動"],
        "advisor": "非常適合海景教堂、懸崖海景台、日落海邊晚宴類型場地。"
    },
    "奢华度假村派 (Luxury Resort)": {
        "title": "🏝 奢华度假村派",
        "desc": "你想要婚禮＝慶典＋旅行＋享受。你重視一站式體驗，唔想辛苦趕行程。",
        "bullets": ["一站式服務", "住宿／泳池／Spa", "賓客可以住埋一齊玩"],
        "advisor": "度假村型場地最 match：同一個地方完成儀式、晚宴同 after party。"
    },
    "文化传统派 (Cultural Heritage)": {
        "title": "🏯 文化传统派",
        "desc": "你尊重儀式同意義感。你追求嘅係『重量』——一場有文化、有故事嘅婚禮。",
        "bullets": ["莊重儀式", "文化氛圍", "有傳承感的場地"],
        "advisor": "特別適合古宅／傳統庭園／文化建築／帶儀式性的場地。"
    },
    "自然隐秘派 (Nature Retreat)": {
        "title": "🌿 自然隐秘派",
        "desc": "你真正想要嘅係安靜、真實、遠離人群。你唔係為展示，而係為咗沉浸體驗。",
        "bullets": ["私隱度高", "寧靜沉浸", "自然環境療癒感"],
        "advisor": "適合隱世 retreat、山谷/森林私密場地、遠離觀光人流的地方。"
    },
    "现代简约派 (Modern Minimalist)": {
        "title": "🖤 现代简约派",
        "desc": "你喜歡俐落、乾淨、有品味。你知道自己要乜，唔鍾意拖泥帶水。",
        "bullets": ["設計感", "方便與效率", "簡約但要好睇"],
        "advisor": "城市精品酒店、現代宴會廳、設計師場地/藝廊風會非常合適。"
    },
    "豪华宴会派 (Luxury Banquet)": {
        "title": "👑 豪华宴会派",
        "desc": "你重視排場、體面同流程完成度。你想呢一日做到最好，賓客體驗要穩陣。",
        "bullets": ["規模與氣派", "SOP與可控性", "家族與賓客感受"],
        "advisor": "五星級酒店 ballroom、頂級會所、可控度高的室內宴會場地最適合你。"
    },
    "特色别墅派 (Unique Villas)": {
        "title": "🏡 特色别墅派",
        "desc": "你想辦一場『像在自己地盤』嘅婚禮：大家放鬆、靠近、玩埋一齊。",
        "bullets": ["包場私密", "親密互動", "after party 氣氛感"],
        "advisor": "獨棟別墅包場、泳池畔證婚、private venue 會令你最舒服。"
    },
    "森林童话派 (Forest Fairytale)": {
        "title": "🌲 森林童话派",
        "desc": "你向往夢幻、故事同照片的魔法。森林、光影、草地——你要嘅係童話感。",
        "bullets": ["浪漫童話氛圍", "自然光影與畫面", "故事感儀式"],
        "advisor": "森林教堂、山谷草地、樹影光斑場景（例如輕井澤系）特別合拍。"
    },
}

# =========================
# 4) UI
# =========================
st.title("🕊️ 尋找您的命定婚禮場地")
st.markdown("### --- Wedding Venue Finder ---")
st.info("回答以下 12 個問題，我們會為你匹配最接近你內心的婚禮場地風格。")

st.markdown('<div class="small">小提示：冇所謂「標準答案」，請用直覺揀。結果會提供主風格＋次風格，並解釋原因。</div>', unsafe_allow_html=True)

# =========================
# 5) Quiz Form (12 questions)
# =========================
with st.form("quiz_form"):
    st.markdown("#### 請開始：")

    q1 = st.radio("Q1 你最夢幻的婚禮畫面是？",
                  ["A 海天一線", "B 森林草地", "C 城市室內", "D 歷史文化建築"], index=None)

    q2 = st.radio("Q2 你想婚禮的規模是？",
                  ["A 只限最親密", "B 小型但熱鬧", "C 中型", "D 盛大排場"], index=None)

    q3 = st.radio("Q3 你對私隱的要求？",
                  ["A 非常重要", "B 希望但可接受其他", "C 不太在意"], index=None)

    q4 = st.radio("Q4 你是否希望婚禮同時是一趟度假？",
                  ["A 必須是", "B 有更好", "C 不需要"], index=None)

    q5 = st.radio("Q5 如果為了美景，需要坐車 1–2 小時，你可以嗎？",
                  ["A 可以", "B 看情況", "C 不可以"], index=None)

    q6 = st.radio("Q6 你理想的風格更像？",
                  ["A 童話浪漫", "B 現代時尚", "C 傳統文化", "D 溫馨派對"], index=None)

    q7 = st.radio("Q7 你希望場地給人的感覺？",
                  ["A 神聖儀式", "B 自然", "C 高端體面", "D 像自己家"], index=None)

    q8 = st.radio("Q8 對戶外變數（天氣/蚊蟲）的接受度？",
                  ["A 完全可以", "B 要備案", "C 不行"], index=None)

    q9 = st.radio("Q9 婚禮後你希望賓客？",
                  ["A 繼續一起玩", "B 方便離開", "C 留在住宿慢慢享受"], index=None)

    q10 = st.radio("Q10 你心中婚禮的關鍵字？",
                   ["A 浪漫", "B 隱世", "C 便利", "D 氣派"], index=None)

    q11 = st.radio("Q11 預算態度更接近？",
                   ["A 可以為體驗加分", "B 控制在合理", "C 高CP值最重要"], index=None)

    q12 = st.radio("Q12 哪句最打動你？",
                   ["A 人生一次的夢", "B 親密與真實", "C 盛大與體面", "D 放鬆與享受"], index=None)

    submitted = st.form_submit_button("✨ 查看我的命定場地 ✨")

# =========================
# 6) Scoring (mapping)
# =========================
if submitted:
    answers = [q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12]
    if not all(answers):
        st.warning("請回答所有問題後再提交喔！")
    else:
        scores = empty_scores()
        reasons = {c: [] for c in CATS}

        # Helper to apply both points & human-readable reason
        def apply(points, reason_text):
            add(scores, points)
            add_reason(reasons, points, reason_text)

        # ---- Q1
        if q1.startswith("A"):
            apply({"海滩婚礼派 (Beach Wedding)": 4, "奢华度假村派 (Luxury Resort)": 1}, "你對海景畫面有明確偏好")
        elif q1.startswith("B"):
            apply({"森林童话派 (Forest Fairytale)": 4, "自然隐秘派 (Nature Retreat)": 2}, "你嚮往森林/草地的自然場景")
        elif q1.startswith("C"):
            apply({"现代简约派 (Modern Minimalist)": 3, "豪华宴会派 (Luxury Banquet)": 2}, "你偏好城市室內、乾淨俐落的場景")
        elif q1.startswith("D"):
            apply({"文化传统派 (Cultural Heritage)": 4, "豪华宴会派 (Luxury Banquet)": 1}, "你被『文化與故事感』吸引")

        # ---- Q2
        if q2.startswith("A"):
            apply({"特色别墅派 (Unique Villas)": 4, "自然隐秘派 (Nature Retreat)": 1}, "你偏好小型、私密的婚禮形式")
        elif q2.startswith("B"):
            apply({"特色别墅派 (Unique Villas)": 3, "森林童话派 (Forest Fairytale)": 1}, "你想親密但又要有熱鬧氣氛")
        elif q2.startswith("C"):
            apply({"现代简约派 (Modern Minimalist)": 2, "奢华度假村派 (Luxury Resort)": 1}, "你接受中型規模，重視平衡")
        elif q2.startswith("D"):
            apply({"豪华宴会派 (Luxury Banquet)": 4}, "你希望有排場與規模感")

        # ---- Q3
        if q3.startswith("A"):
            apply({"特色别墅派 (Unique Villas)": 3, "自然隐秘派 (Nature Retreat)": 3}, "你非常在意私隱與不被打擾")
        elif q3.startswith("B"):
            apply({"森林童话派 (Forest Fairytale)": 1, "奢华度假村派 (Luxury Resort)": 1}, "你在意私隱，但也願意為體驗作取捨")
        elif q3.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 2}, "你較不介意人流與公開感")

        # ---- Q4
        if q4.startswith("A"):
            apply({"奢华度假村派 (Luxury Resort)": 4, "海滩婚礼派 (Beach Wedding)": 1}, "你希望婚禮同時是一趟舒服的旅行")
        elif q4.startswith("B"):
            apply({"森林童话派 (Forest Fairytale)": 1, "特色别墅派 (Unique Villas)": 1}, "你喜歡度假感，但不一定要一站式")
        elif q4.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 2, "现代简约派 (Modern Minimalist)": 1}, "你更重視典禮本身與流程效率")

        # ---- Q5
        if q5.startswith("A"):
            apply({"森林童话派 (Forest Fairytale)": 2, "自然隐秘派 (Nature Retreat)": 2, "海滩婚礼派 (Beach Wedding)": 1}, "你願意為美景移動，重視場景價值")
        elif q5.startswith("B"):
            apply({"奢华度假村派 (Luxury Resort)": 1}, "你可接受移動，但希望安排合理")
        elif q5.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 3, "现代简约派 (Modern Minimalist)": 1}, "你重視交通便利與可控性")

        # ---- Q6
        if q6.startswith("A"):
            apply({"森林童话派 (Forest Fairytale)": 4, "海滩婚礼派 (Beach Wedding)": 1}, "你向往童話浪漫的氛圍")
        elif q6.startswith("B"):
            apply({"现代简约派 (Modern Minimalist)": 4}, "你偏好現代、設計感與簡約美學")
        elif q6.startswith("C"):
            apply({"文化传统派 (Cultural Heritage)": 4}, "你重視傳統文化與儀式感")
        elif q6.startswith("D"):
            apply({"特色别墅派 (Unique Villas)": 3, "奢华度假村派 (Luxury Resort)": 1}, "你想要溫馨、熱鬧、像派對般的體驗")

        # ---- Q7
        if q7.startswith("A"):
            apply({"海滩婚礼派 (Beach Wedding)": 2, "文化传统派 (Cultural Heritage)": 1}, "你重視神聖與儀式氛圍")
        elif q7.startswith("B"):
            apply({"森林童话派 (Forest Fairytale)": 2, "自然隐秘派 (Nature Retreat)": 1}, "你最想要自然感與放鬆氣息")
        elif q7.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 3}, "你需要高端體面與完成度")
        elif q7.startswith("D"):
            apply({"特色别墅派 (Unique Villas)": 3}, "你想像在自己家一樣自在")

        # ---- Q8
        if q8.startswith("A"):
            apply({"森林童话派 (Forest Fairytale)": 2, "自然隐秘派 (Nature Retreat)": 1}, "你能接受戶外的自然變數")
        elif q8.startswith("B"):
            apply({"奢华度假村派 (Luxury Resort)": 2}, "你想要戶外感，但必須有備案")
        elif q8.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 3, "现代简约派 (Modern Minimalist)": 1}, "你偏好室內舒適與可控")

        # ---- Q9
        if q9.startswith("A"):
            apply({"特色别墅派 (Unique Villas)": 3, "奢华度假村派 (Luxury Resort)": 1}, "你想婚禮後繼續一起玩，重視互動")
        elif q9.startswith("B"):
            apply({"现代简约派 (Modern Minimalist)": 1, "豪华宴会派 (Luxury Banquet)": 1}, "你希望散場方便、流程乾淨")
        elif q9.startswith("C"):
            apply({"奢华度假村派 (Luxury Resort)": 3}, "你想大家住埋一齊慢慢享受")

        # ---- Q10
        if q10.startswith("A"):
            apply({"海滩婚礼派 (Beach Wedding)": 2, "森林童话派 (Forest Fairytale)": 1}, "你最在意『浪漫』氛圍")
        elif q10.startswith("B"):
            apply({"自然隐秘派 (Nature Retreat)": 3, "特色别墅派 (Unique Villas)": 1}, "你被『隱世』與私密感吸引")
        elif q10.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 2, "现代简约派 (Modern Minimalist)": 2}, "你把『便利』放在首位")
        elif q10.startswith("D"):
            apply({"豪华宴会派 (Luxury Banquet)": 4}, "你追求氣派與規模感")

        # ---- Q11
        if q11.startswith("A"):
            apply({"奢华度假村派 (Luxury Resort)": 2, "海滩婚礼派 (Beach Wedding)": 1}, "你願意為體驗與享受付出")
        elif q11.startswith("B"):
            apply({"现代简约派 (Modern Minimalist)": 1, "文化传统派 (Cultural Heritage)": 1}, "你希望在質感與預算之間取得平衡")
        elif q11.startswith("C"):
            apply({"特色别墅派 (Unique Villas)": 1, "森林童话派 (Forest Fairytale)": 1}, "你更重視CP值與花錢的『重點』")

        # ---- Q12
        if q12.startswith("A"):
            apply({"森林童话派 (Forest Fairytale)": 2, "海滩婚礼派 (Beach Wedding)": 1}, "你想要一場人生一次的夢幻感")
        elif q12.startswith("B"):
            apply({"特色别墅派 (Unique Villas)": 2, "自然隐秘派 (Nature Retreat)": 1}, "你最重視親密與真實交流")
        elif q12.startswith("C"):
            apply({"豪华宴会派 (Luxury Banquet)": 3}, "你希望盛大體面、賓客感受要到位")
        elif q12.startswith("D"):
            apply({"奢华度假村派 (Luxury Resort)": 3}, "你想用放鬆與享受完成這一日")

        # =========================
        # 7) Final result
        # =========================
        top2_list, sorted_all = top2(scores)
        (best_cat, best_score) = top2_list[0]
        (second_cat, second_score) = top2_list[1]
        diff = best_score - second_score

        # Clean reasons: unique + take top 4
        best_reasons = list(dict.fromkeys(reasons[best_cat]))[:4]

        st.balloons()
        st.success(f"✨ 你的主推薦風格：**{RESULT_COPY[best_cat]['title']}**  （得分 {best_score}）")
        st.info(f"💡 次推薦風格：**{RESULT_COPY[second_cat]['title']}**  （得分 {second_score}）")
        st.write(f"**風格強度：{strength_label(diff)}**")

        # Result card
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"**{RESULT_COPY[best_cat]['desc']}**")
        st.markdown("**你重視：**")
        for b in RESULT_COPY[best_cat]["bullets"]:
            st.write(f"• {b}")
        st.markdown("**為甚麼我哋咁判斷（根據你嘅答案）：**")
        for r in best_reasons:
            st.write(f"• {r}")
        st.markdown(f"**Love’s On 顧問建議：** {RESULT_COPY[best_cat]['advisor']}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")
        st.markdown("### 📩 想獲得你的專屬場地清單？（可選）")
        st.caption("你可以留低聯絡方式，我哋會按你的主/次風格準備 Top 5 推薦場地＋預算範圍。")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("你的稱呼（可選）")
        with col2:
            contact = st.text_input("WhatsApp / Email（可選）")

        if contact:
            st.success("收到！你可以把結果截圖 send 畀我哋，或直接留言你最想去日本定峇里島，我哋會更快整理 proposal。")

        st.write("---")
        with st.expander("🔎 查看全部得分（Debug）"):
            for k, v in sorted_all:
                st.write(f"{k}: {v}")
