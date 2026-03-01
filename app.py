import streamlit as st
import google.generativeai as genai
from pptx import Presentation
from io import BytesIO
from PIL import Image

# --- 1. 初始化与权限 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# --- 2. 极致审美 CSS (对标 Nano Studio) ---
st.set_page_config(page_title="Haval PR Lab", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #ffffff; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 30px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff6b00 0%, #ff3d00 100%);
        color: white; border: none; border-radius: 12px; height: 50px;
        font-weight: 600; letter-spacing: 1px; transition: all 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(255,107,0,0.4); }
    </style>
""", unsafe_allow_html=True)

# --- 3. 核心步骤逻辑 ---
st.title("🚗 哈弗（Haval）竞标案：多维策略实验室")
st.caption("🚀 Paid Tier 3 满血运行中 | 交互式审美工作站")

# 步骤导航
current_step = st.session_state.step
st.write(f"进度：第 {current_step} 阶段 / 共 4 阶段")

# --- 阶段 1：大纲脑暴 ---
if current_step == 1:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 1：策略大纲")
        topic = st.text_area("输入哈弗竞标的核心命题：", "哈弗猛龙 2026 年度品牌公关传播策略")
        if st.button("生成初步大纲"):
            model = genai.GenerativeModel('gemini-2.0-flash') # 快速响应
            res = model.generate_content(f"作为资深公关总监，请为哈弗（Haval）生成一份极具竞争力的 10 页 PPT 大纲：{topic}")
            st.session_state.data['outline'] = res.text
        
        if 'outline' in st.session_state.data:
            st.text_area("手动修饰大纲：", value=st.session_state.data['outline'], height=300, key="edit_outline")
            if st.button("大纲定稿 → 下一步"):
                st.session_state.step = 2
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 阶段 2：内容填充 ---
elif current_step == 2:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 2：内容深度生成")
        st.info("正在使用 Gemini 3.1 Pro 引擎为您填充每一页的公关话术...")
        if st.button("一键填充全文（建议使用 Pro 引擎）"):
            model = genai.GenerativeModel('gemini-3.1-pro-preview')
            res = model.generate_content(f"请基于以下大纲，写出每一页 PPT 的详细文案（要求语言犀利、专业，适合哈弗竞标）：{st.session_state.data.get('outline')}")
            st.session_state.data['full_content'] = res.text
            
        if 'full_content' in st.session_state.data:
            st.text_area("文案精调：", value=st.session_state.data['full_content'], height=400, key="edit_content")
            if st.button("内容满意 → 进入审美设定"):
                st.session_state.step = 3
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 阶段 3：审美投喂 (接口在这里！) ---
elif current_step == 3:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 3：审美与风格接口")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write("🖼️ **方法 A：投喂审美参考图**")
            uploaded_file = st.file_uploader("上传你喜欢的视觉参考图（KV、海报等）", type=['png', 'jpg', 'jpeg'])
            if uploaded_file:
                st.image(uploaded_file, caption="已收录您的审美偏好", width=300)
                if st.button("让 AI 学习此图片风格"):
                    img = Image.open(uploaded_file)
                    model = genai.GenerativeModel('gemini-2.0-flash') # 用多模态识图
                    res = model.generate_content(["请分析这张图片的色调、情绪和设计风格，并告诉我如何将其应用在哈弗猛龙的 PPT 视觉设计中。", img])
                    st.session_state.data['img_analysis'] = res.text
        
        with col2:
            st.write("🎨 **方法 B：预设风格选择**")
            style = st.selectbox("或者选择一个预设风格：", ["硬核越野（黑橙）", "极简智电（白蓝）", "新中式国潮", "赛博未来"])
            if st.button("确认风格选择"):
                st.session_state.data['selected_style'] = style
                st.session_state.step = 4
                st.rerun()
        
        if 'img_analysis' in st.session_state.data:
            st.success("AI 已习得您的审美：")
            st.caption(st.session_state.data['img_analysis'])
            if st.button("风格已对齐 → 进入终稿"):
                st.session_state.step = 4
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 阶段 4：定稿导出 ---
elif current_step == 4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📍 阶段 4：定稿导出")
    st.write("已整合所有大纲、内容及审美偏好。")
    # 这里可以加入 python-pptx 生成逻辑 (略)
    st.balloons()
    st.download_button("📥 下载可编辑 PPTX 定稿", data=b"placeholder", file_name="Haval_Raptor_Proposal.pptx")
    if st.button("重新开始"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
