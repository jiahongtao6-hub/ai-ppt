import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 动力系统：锁定 2026 满血版模型 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化状态
if 'messages' not in st.session_state: st.session_state.messages = []
if 'ppt_content' not in st.session_state: st.session_state.ppt_content = "### 🚗 哈弗猛龙：智电越野新标杆\n---\n**等待您的创意指令...**"
if 'current_vibe' not in st.session_state: st.session_state.current_vibe = "默认专业"

# --- 2. 审美重塑：沉浸式卡片 UI ---
st.set_page_config(page_title="Nano Studio", layout="wide")
st.markdown(f"""
    <style>
    .stApp {{ background-color: #fcfcfc; }}
    section[data-testid="stSidebar"] {{ background-color: white !important; border-right: 1px solid #eee; width: 400px !important; }}
    /* PPT 幻灯片容器 - 修复渲染核心 */
    .slide-box {{
        background: white;
        border-radius: 16px;
        padding: 60px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
        min-height: 500px;
        color: #333;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：对话沟通 ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    chat_container = st.container(height=400)
    for m in st.session_state.messages:
        chat_container.chat_message(m["role"]).write(m["content"])
    
    st.markdown("---")
    st.write("🎨 **风格库**")
    c1, c2 = st.columns(2)
    if c1.button("🔥 硬核越野", use_container_width=True): st.session_state.current_vibe = "硬核黑橙"
    if c2.button("⚡ 智电科技", use_container_width=True): st.session_state.current_vibe = "智电极简"
    
    ref_img = st.file_uploader("🖼️ 投喂参考图 (可选)", type=['png', 'jpg'])
    
    if user_input := st.chat_input("对我下达指令..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("思考中..."):
            # 锁定 2.5-flash，解决 404 问题
            model = genai.GenerativeModel('gemini-2.5-flash') 
            prompt = f"你是哈弗公关专家。根据需求'{user_input}'和风格'{st.session_state.current_vibe}'，写出PPT页面的核心内容。请直接使用 Markdown 格式。"
            
            try:
                if ref_img:
                    res = model.generate_content([prompt, Image.open(ref_img)])
                else:
                    res = model.generate_content(prompt)
                
                st.session_state.ppt_content = res.text
                st.session_state.messages.append({"role": "assistant", "content": "内容已更新至右侧。"})
                st.rerun()
            except Exception as e:
                st.error(f"连接异常: {e}")

# --- 4. 右侧：PPT 实时预览 ---
st.subheader("PPT 实时预览")
st.caption(f"当前审美基调：{st.session_state.current_vibe}")

# 核心修复：使用 st.container 配合内部 markdown 确保内容在框内
with st.container(border=True):
    st.markdown(st.session_state.ppt_content)

# 功能栏
st.markdown("---")
b1, b2, b3, _ = st.columns([1, 1, 1, 3])
if b1.button("✨ 深度润色 (3.1 Pro)"):
    with st.spinner("正在润色..."):
        pro = genai.GenerativeModel('gemini-3.1-pro-preview')
        res = pro.generate_content(f"专业润色哈弗竞标文案：{st.session_state.ppt_content}")
        st.session_state.ppt_content = res.text
        st.rerun()

b2.button("👁️ 演示模式")
b3.download_button("📥 导出 PPTX", data="...", file_name="Haval.pptx")
