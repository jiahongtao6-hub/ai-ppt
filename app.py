import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：多模型分级策略 (省 Token 关键) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化状态
if 'chat' not in st.session_state: st.session_state.chat = []
if 'preview' not in st.session_state: st.session_state.preview = {"title": "等待构思...", "body": ""}
if 'style' not in st.session_state: st.session_state.style = "未设定"

# --- 2. 界面审美：Nano Studio 洁白纯净风 ---
st.set_page_config(page_title="Haval PR Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #333; }
    /* 对话框样式 */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #eee; width: 400px !important; }
    /* 卡片式预览 */
    .ppt-frame {
        background: white; border-radius: 12px; padding: 50px;
        box-shadow: 0 15px 45px rgba(0,0,0,0.08); border: 1px solid #efefef;
        min-height: 550px; margin-top: 20px;
    }
    .stButton>button { border-radius: 10px; height: 45px; font-weight: 600; }
    .main-btn { background: #28a745 !important; color: white !important; border: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧交互区：对话即生产 ---
with st.sidebar:
    st.title("🦔 Nano Studio") # 刺猬 IP 精神寄托
    st.caption("🚀 Paid Tier 3 满血版 | 省 Token 模式已开启")
    
    # 对话流展示
    chat_box = st.container(height=400)
    for m in st.session_state.chat:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    # 交互式功能区
    st.markdown("---")
    st.write("🎨 **风格预设**")
    cols = st.columns(2)
    if cols[0].button("🔥 硬核越野", use_container_width=True): 
        st.session_state.style = "硬核越野（黑橙）"
        st.session_state.chat.append({"role": "assistant", "content": "收到，视觉风格已锁定：硬核越野。"})
    if cols[1].button("⚡ 智电科技", use_container_width=True): 
        st.session_state.style = "极简科技（白蓝）"
        st.session_state.chat.append({"role": "assistant", "content": "收到，视觉风格已锁定：极简智电。"})
    
    ref_img = st.file_uploader("🖼️ 投喂参考图 (可选)", type=['png', 'jpg'])
    
    # 聊天输入
    if user_input := st.chat_input("说出你的哈弗竞标想法..."):
        st.session_state.chat.append({"role": "user", "content": user_input})
        
        with st.spinner("AI 正在构思..."):
            # 默认使用 Flash 以节省 Token
            model = genai.GenerativeModel('models/gemini-2.0-flash')
            
            # 多模态处理
            prompt = f"你现在是哈弗公关总监。针对需求：'{user_input}'，当前风格：'{st.session_state.style}'，请更新 PPT 预览内容。如果是构思大纲，请分条列出；如果是内容填充，请精准专业。"
            
            if ref_img:
                img = Image.open(ref_img)
                response = model.generate_content([prompt, img])
            else:
                response = model.generate_content(prompt)
            
            st.session_state.preview["body"] = response.text
            st.session_state.chat.append({"role": "assistant", "content": "已根据您的建议更新了右侧预览。"})
            st.rerun()

# --- 4. 右侧预览区：沉浸式预览 ---
st.subheader("生成的 PPT 预览")
st.caption(f"当前审美基调：{st.session_state.style}")

with st.container():
    st.markdown('<div class="ppt-frame">', unsafe_allow_html=True)
    st.write(st.session_state.preview["body"])
    st.markdown('</div>', unsafe_allow_html=True)

# 底部动作条
st.markdown("---")
b_cols = st.columns([1, 1, 1, 3])
if b_cols[0].button("✨ 深度润色 (消耗 Pro)"):
    # 只有用户主动点润色，才动用高成本模型
    pro_model = genai.GenerativeModel('models/gemini-3.1-pro-preview')
    st.session_state.preview["body"] = pro_model.generate_content(f"请用极其专业的公关措辞润色这段哈弗竞标内容：{st.session_state.preview['body']}").text
    st.rerun()

b_cols[1].button("👁️ 演示预览", use_container_width=True)
b_cols[2].download_button("📥 导出 PPTX", data="...", file_name="Haval_Proposal.pptx", use_container_width=True)
