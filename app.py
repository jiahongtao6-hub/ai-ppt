import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：基于诊断清单的精准调用 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化持久化状态
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'ppt_view' not in st.session_state: st.session_state.ppt_view = "✨ 正在等待您的第一个创意..."
if 'vibe' not in st.session_state: st.session_state.vibe = "默认专业"

# --- 2. 界面审美：沉浸式 Nano Studio 风格 ---
st.set_page_config(page_title="Nano PPT Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; color: #1a1a1a; }
    /* 左侧对话面板 */
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #e9ecef; width: 420px !important; }
    /* 预览画板 */
    .preview-canvas {
        background: white; border-radius: 16px; padding: 40px;
        box-shadow: 0 12px 40px rgba(0,0,0,0.06); border: 1px solid #eee;
        min-height: 580px; transition: 0.3s;
    }
    /* 风格卡片交互 */
    .stButton>button { border-radius: 10px; border: 1px solid #ddd; background: white; transition: 0.2s; }
    .stButton>button:hover { border-color: #ff6b00; color: #ff6b00; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：对话式创意入口 ---
with st.sidebar:
    st.markdown("### 🦔 Nano PPT Lab")
    st.caption("🚀 Paid Tier 3 | 自动节流模式已开启")
    
    # 聊天历史流
    chat_box = st.container(height=420)
    for m in st.session_state.chat_log:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    # 风格库：点选即生效
    st.markdown("---")
    st.write("🎨 **风格库**")
    s_cols = st.columns(2)
    if s_cols[0].button("🔥 硬核越野", use_container_width=True): 
        st.session_state.vibe = "硬核黑橙"; st.toast("风格已锁定：硬核越野")
    if s_cols[1].button("⚡ 智电科技", use_container_width=True): 
        st.session_state.vibe = "智电极简"; st.toast("风格已锁定：智电科技")
    
    # 图片喂口 (完全可选)
    ref_pic = st.file_uploader("🖼️ 投喂参考图 (可选)", type=['png', 'jpg'])
    
    # 对话驱动
    if user_cmd := st.chat_input("对我下达哈弗方案指令..."):
        st.session_state.chat_log.append({"role": "user", "content": user_cmd})
        with st.spinner("思考中..."):
            # 默认使用极速 Flash 节省 Token
            model = genai.GenerativeModel('gemini-2.0-flash') 
            
            prompt = f"你是哈弗竞标专家。用户要求：'{user_cmd}'，风格设定：'{st.session_state.vibe}'。请据此更新 PPT 方案，语言要专业。直接输出内容，不要废话。"
            
            try:
                if ref_pic:
                    img = Image.open(ref_pic)
                    res = model.generate_content([prompt, img])
                else:
                    res = model.generate_content(prompt)
                
                st.session_state.ppt_view = res.text
                st.session_state.chat_log.append({"role": "assistant", "content": "方案已实时同步至画板。"})
                st.rerun()
            except Exception as e:
                st.error(f"模型通讯异常，请确认项目配置：{e}")

# --- 4. 右侧：沉浸式内容画板 ---
st.markdown(f"#### 生成的 PPT 页面 预览")
st.caption(f"当前审美基调：{st.session_state.vibe}")

with st.container():
    st.markdown('<div class="preview-canvas">', unsafe_allow_html=True)
    st.markdown(st.session_state.ppt_view)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部生产力工具
st.markdown("---")
t1, t2, t3, _ = st.columns([1, 1, 1, 3])
if t1.button("✨ 深度润色 (Pro)"):
    # 只有点击润色时才动用 3.1 Pro 顶级引擎
    with st.spinner("正在启动 3.1 Pro 核心逻辑..."):
        pro = genai.GenerativeModel('gemini-3.1-pro-preview')
        refined = pro.generate_content(f"请用极其犀利、专业的公关竞标笔触润色以下内容：{st.session_state.ppt_view}")
        st.session_state.ppt_view = refined.text
        st.rerun()

t2.button("👁️ 全屏演示", use_container_width=True)
t3.download_button("📥 导出 PPTX", data="...", file_name="Haval_Raptor.pptx", use_container_width=True)
