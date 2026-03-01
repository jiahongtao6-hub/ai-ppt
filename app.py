import streamlit as st
import google.generativeai as genai
from PIL import Image
import base64

# --- 1. 动力系统：锁定 2026 顶级 Imagen 4.0 接口 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化状态
if 'history' not in st.session_state: st.session_state.history = []
if 'ppt_text' not in st.session_state: st.session_state.ppt_text = "✨ 正在等待您的第一个哈弗创意..."
if 'slide_img' not in st.session_state: st.session_state.slide_img = None

# --- 2. 审美重构：Nano Studio 极致极简风 ---
st.set_page_config(page_title="Haval Visual Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; color: #1a1a1a; }
    section[data-testid="stSidebar"] { background-color: #f8f9fa !important; border-right: 1px solid #eee; width: 420px !important; }
    /* 画板容器 */
    .canvas {
        background: #fdfdfd; border-radius: 20px; border: 1px solid #eaeaea;
        box-shadow: 0 20px 60px rgba(0,0,0,0.05); overflow: hidden; min-height: 600px;
    }
    .img-area { height: 400px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; overflow: hidden; }
    .text-area { padding: 40px; font-family: "Microsoft YaHei", sans-serif; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通台 (左) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 聊天记录
    for m in st.session_state.history:
        st.chat_message(m["role"]).write(m["content"])
    
    # 风格快捷点选
    st.markdown("---")
    st.write("🎨 **风格预设**")
    cols = st.columns(2)
    offroad = cols[0].button("🔥 硬核越野")
    tech = cols[1].button("⚡ 智电科技")
    
    # 指令输入
    if prompt := st.chat_input("说出你的方案需求，比如：给猛龙做张夕阳山地的竞标KV"):
        st.session_state.history.append({"role": "user", "content": prompt})
        
        with st.spinner("AI 正在深度思考并构图..."):
            # 1. 生成文案 (使用 Flash 节省 Token)
            txt_model = genai.GenerativeModel('gemini-2.5-flash')
            txt_res = txt_model.generate_content(f"你是哈弗公关专家。根据需求'{prompt}'，为PPT页面写出极具煽动性的文案，并构思一张KV视觉图的描述词。")
            st.session_state.ppt_text = txt_res.text
            
            # 2. 自动绘图 (锁定 Imagen 4.0 顶级模型)
            try:
                # 2026 版新调用方式：通过 GenerativeModel 直接呼叫 imagen 系列
                img_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                # 提取 AI 构思的视觉描述
                img_res = img_model.generate_content(f"Create a high-end PR Key Visual for Haval Raptor SUV based on: {prompt}. Cinematic lighting, professional photography style, 8k.")
                # 获取图片对象
                if img_res.candidates[0].content.parts[0].inline_data:
                    img_data = img_res.candidates[0].content.parts[0].inline_data.data
                    st.session_state.slide_img = img_data
                st.session_state.history.append({"role": "assistant", "content": "已为您生成视觉大片与文案。"})
            except Exception as e:
                st.error(f"视觉引擎连接中: {e}")
        st.rerun()

# --- 4. 右侧：沉浸式方案画板 (右) ---
st.subheader("PPT 页面即时预览")

with st.container():
    st.markdown('<div class="canvas">', unsafe_allow_html=True)
    
    # 上半部分：KV 视觉区
    if st.session_state.slide_img:
        st.image(st.session_state.slide_img, use_container_width=True)
    else:
        st.markdown('<div class="img-area">🖼️ 在左侧输入指令，我将为您绘制哈弗竞标级 KV</div>', unsafe_allow_html=True)
    
    # 下半部分：文案内容区
    st.markdown('<div class="text-area">', unsafe_allow_html=True)
    st.markdown(st.session_state.ppt_text)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 底部：总监级润色
if st.button("✨ 深度润色并增强画质 (3.1 Pro + Imagen 4.0 Ultra)"):
    with st.spinner("顶级总监介入中..."):
        pro = genai.GenerativeModel('gemini-3.1-pro-preview')
        st.session_state.ppt_text = pro.generate_content(f"专业润色哈弗竞标文案：{st.session_state.ppt_text}").text
        st.rerun()
