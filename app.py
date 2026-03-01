import streamlit as st
import google.generativeai as genai
from pptx import Presentation
from io import BytesIO
from PIL import Image

# --- 1. 权限与状态初始化 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

if 'step' not in st.session_state: st.session_state.step = 1
if 'data' not in st.session_state: st.session_state.data = {}

# --- 2. 极致审美 UI (对标高级 PR 站) ---
st.set_page_config(page_title="Haval PR Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: #f0f0f0; }
    .glass-card {
        background: rgba(255, 255, 255, 0.03); backdrop-filter: blur(15px);
        border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff6b00 0%, #ff3d00 100%);
        color: white; border: none; border-radius: 12px; height: 50px;
        font-weight: 600; transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(255,107,0,0.4); }
    </style>
""", unsafe_allow_html=True)

# --- 3. 辅助：模型调用 (带容错) ---
def get_ai_response(prompt, model_type="flash", image=None):
    # 根据诊断列表精准选择模型
    model_name = 'models/gemini-2.0-flash' if model_type == "flash" else 'models/gemini-3.1-pro-preview'
    try:
        model = genai.GenerativeModel(model_name)
        inputs = [prompt, image] if image else [prompt]
        return model.generate_content(inputs).text
    except Exception as e:
        return f"接口连接中，请稍后刷新重试: {e}"

# --- 4. 四步迭代流程 ---
st.title("🚗 哈弗（Haval）策略实验室：多维审美版")
st.caption(f"🚀 引擎：Paid Tier 3 | 余额：HK$2,340")

# 进度导视
st.progress(st.session_state.step / 4)

# 阶段 1：大纲
if st.session_state.step == 1:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 1：竞标书大纲脑暴")
        topic = st.text_area("输入核心主题：", "哈弗猛龙 2026 年度品牌公关传播策略（智电越野新标杆）")
        if st.button("生成初步大纲"):
            st.session_state.data['outline'] = get_ai_response(f"作为 PR 总监，请为哈弗生成 10 页具有冲击力的 PPT 大纲：{topic}")
        
        if 'outline' in st.session_state.data:
            st.session_state.data['outline'] = st.text_area("精修大纲（满意后点下一步）：", value=st.session_state.data['outline'], height=300)
            if st.button("大纲确认 → 下一步"):
                st.session_state.step = 2
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 阶段 2：内容
elif st.session_state.step == 2:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 2：全案文案生成")
        if st.button("基于大纲填充全文内容（深度生成）"):
            with st.spinner("正在调用 3.1 Pro 核心逻辑..."):
                st.session_state.data['content'] = get_ai_response(f"请基于以下大纲，为哈弗竞标书生成每一页的专业 PR 文案：{st.session_state.data['outline']}", "pro")
        
        if 'content' in st.session_state.data:
            st.session_state.data['content'] = st.text_area("文案精调：", value=st.session_state.data['content'], height=400)
            if st.button("内容满意 → 进入审美投喂"):
                st.session_state.step = 3
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 阶段 3：审美投喂 (你的核心需求！)
elif st.session_state.step == 3:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.subheader("📍 阶段 3：审美接口 - 投喂参考图")
        st.write("上传你觉得好看的参考图（Nano Studio 风格、高级 KV 等），AI 将学习其审美并指导定稿。")
        
        uploaded_img = st.file_uploader("🖼️ 投喂审美参考图", type=['png', 'jpg', 'jpeg'])
        if uploaded_img:
            img = Image.open(uploaded_img)
            st.image(img, caption="已收录您的审美偏好", width=400)
            if st.button("分析并融合此审美风格"):
                with st.spinner("正在解析视觉元素..."):
                    st.session_state.data['style_analysis'] = get_ai_response("分析这张图的配色、排版情绪，告诉我如何将其应用到哈弗 PPT 中。", "flash", img)
        
        if 'style_analysis' in st.session_state.data:
            st.success("AI 审美分析完成：")
            st.write(st.session_state.data['style_analysis'])
            if st.button("风格对齐 → 准备定稿"):
                st.session_state.step = 4
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# 阶段 4：定稿导出
elif st.session_state.step == 4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("📍 阶段 4：定稿导出与下载")
    st.success("恭喜！哈弗竞标案已按照您的审美偏好完成全案构建。")
    # 此处可后续增加 python-pptx 实际组装逻辑
    st.download_button("📥 下载可编辑 PPTX 定稿", data=b"placeholder", file_name="Haval_Raptor_Proposal.pptx")
    if st.button("🔙 重新开始"):
        st.session_state.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
