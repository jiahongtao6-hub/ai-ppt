import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：基于 2026 账号诊断的精准模型 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化状态
if 'messages' not in st.session_state: st.session_state.messages = []
if 'draft' not in st.session_state: st.session_state.draft = "✨ 说出你的哈弗创意，方案将在此处实时成形..."
if 'vibe' not in st.session_state: st.session_state.vibe = "默认专业"

# --- 2. 审美重塑：对标 Nano Studio 纯净感 ---
st.set_page_config(page_title="Haval PR Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #333; }
    /* 左侧对话流 */
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #eee; width: 450px !important; }
    /* 右侧 PPT 画板 */
    .ppt-canvas {
        background: white; border-radius: 12px; padding: 40px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.04); border: 1px solid #efefef;
        min-height: 600px; line-height: 1.6;
    }
    .stButton>button { border-radius: 8px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通区 ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption("🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 聊天记录
    chat_container = st.container(height=450)
    for m in st.session_state.messages:
        chat_container.chat_message(m["role"]).write(m["content"])
    
    # 风格预设（点选即生效，不强迫喂图）
    st.markdown("---")
    st.write("🎨 **风格库**")
    c1, c2 = st.columns(2)
    if c1.button("🔥 硬核越野"): st.session_state.vibe = "硬核黑橙"; st.toast("风格已同步")
    if c2.button("⚡ 智电科技"): st.session_state.vibe = "智电极简"; st.toast("风格已同步")
    
    # 喂图接口（完全可选）
    ref_img = st.file_uploader("🖼️ 投喂审美参考 (可选)", type=['png', 'jpg'])
    
    # 对话驱动
    if user_input := st.chat_input("聊聊你的哈弗竞标需求..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("思考中..."):
            # 【核心修正】：使用你账号支持的 2.5-flash，极快且省钱
            model = genai.GenerativeModel('gemini-2.5-flash') 
            
            prompt = f"你是一位哈弗公关专家。基于需求：'{user_input}'，当前视觉风格：'{st.session_state.vibe}'。请生成或修改 PPT 方案，直接给出干货内容。"
            
            try:
                if ref_img:
                    img = Image.open(ref_img)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                st.session_state.draft = response.text
                st.session_state.messages.append({"role": "assistant", "content": "方案已在右侧预览区更新。"})
                st.rerun()
            except Exception as e:
                st.error(f"通讯异常，请确认模型名：{e}")

# --- 4. 右侧：沉浸式方案预览 ---
st.subheader("PPT 实时预览")
st.caption(f"当前审美基调：{st.session_state.vibe}")

with st.container():
    st.markdown('<div class="ppt-canvas">', unsafe_allow_html=True)
    st.markdown(st.session_state.draft)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部生产力工具
st.markdown("---")
b1, b2, b3, _ = st.columns([1, 1, 1, 3])
if b1.button("✨ 深度润色 (3.1 Pro)"):
    # 只有点润色才动用最贵的顶级引擎
    with st.spinner("顶级总监正在审稿..."):
        pro = genai.GenerativeModel('gemini-3.1-pro-preview')
        res = pro.generate_content(f"请用公关竞标的口吻润色这段哈弗方案：{st.session_state.draft}")
        st.session_state.draft = res.text
        st.rerun()

b2.button("👁️ 演示模式")
b3.download_button("📥 导出 PPTX", data="...", file_name="Haval_Proposal.pptx")
