import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：Paid Tier 3 顶级引擎 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 状态管理
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'ppt_content' not in st.session_state: st.session_state.ppt_content = "等待生成大纲..."
if 'style_lib' not in st.session_state: st.session_state.style_lib = "默认简约"

# --- 2. 审美重塑：Nano Studio 极简风 CSS ---
st.set_page_config(page_title="Nano PPT Lab", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #333; }
    /* 左侧聊天区域 */
    section[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; width: 450px !important; }
    /* 风格卡片网格 */
    .style-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
    .style-card {
        padding: 15px; border-radius: 12px; text-align: center;
        background: #f8f9fa; border: 1px solid #eee; transition: 0.3s; cursor: pointer;
    }
    .style-card:hover { border-color: #28a745; background: #f0fff4; }
    /* PPT 预览区 */
    .ppt-preview {
        background: white; border-radius: 8px; border: 1px solid #ddd;
        box-shadow: 0 10px 30px rgba(0,0,0,0.05); padding: 40px; min-height: 500px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. 侧边栏：对话式交互 (左) ---
with st.sidebar:
    st.image("https://img.icons8.com/color/96/hedgehog.png", width=50) # 加入你的刺猬 IP 小彩蛋
    st.subheader("PPT 视觉设计助手")
    st.caption("🚀 Paid Tier 3 满血版 | 余额: HK$2,340")
    
    # 聊天记录展示
    chat_container = st.container(height=450)
    for msg in st.session_state.chat_history:
        chat_container.chat_message(msg["role"]).write(msg["content"])
    
    # 风格快捷入口
    st.markdown("---")
    st.write("🎨 **风格库 (点选或喂图)**")
    c1, c2 = st.columns(2)
    if c1.button("🔥 硬核越野"): st.session_state.style_lib = "黑橙硬核"; st.toast("风格已选定：硬核越野")
    if c2.button("⚡ 智电科技"): st.session_state.style_lib = "白蓝科技"; st.toast("风格已选定：智电科技")
    
    uploaded_file = st.file_uploader("🖼️ 投喂审美参考图 (可选)", type=['png', 'jpg'])
    
    # 底部输入框
    user_input = st.chat_input("跟我聊聊你的哈弗方案需求...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.spinner("思考中..."):
            model = genai.GenerativeModel('gemini-2.0-flash') # 用 2.0 保证对话流畅度
            prompt = f"你是一位哈弗公关专家。基于用户需求'{user_input}'，参考风格'{st.session_state.style_lib}'，请生成或修改 PPT 大纲，并给出具体的视觉建议。"
            
            # 如果有图片，启用多模态理解
            if uploaded_file:
                img = Image.open(uploaded_file)
                response = model.generate_content([prompt, img])
            else:
                response = model.generate_content(prompt)
            
            st.session_state.ppt_content = response.text
            st.session_state.chat_history.append({"role": "assistant", "content": "方案已更新，请在右侧预览。"})
            st.rerun()

# --- 4. 主界面：生成的 PPT 页面 (右) ---
col_main, _ = st.columns([10, 0.1])
with col_main:
    st.markdown("### 生成的 PPT 页面")
    st.caption(f"当前选定基调：{st.session_state.style_lib}")
    
    with st.container(border=True):
        st.markdown(f'<div class="ppt-preview">', unsafe_allow_html=True)
        # 根据不同阶段展示内容
        st.write(st.session_state.ppt_content)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.button("👁️ 演示模式")
    c2.button("✨ 自动润色")
    c3.download_button("📥 导出 PDF / PPTX", data="...", file_name="Haval_Proposal.pptx")
