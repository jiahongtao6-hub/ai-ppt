import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# --- 1. 动力系统：整合文本与视觉双引擎 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

if 'ppt_content' not in st.session_state: st.session_state.ppt_content = "### 🚗 哈弗猛龙：智电越野新标杆\n---\n**等待输入创意...**"
if 'kv_image' not in st.session_state: st.session_state.kv_image = None

# --- 2. 界面重塑：全屏沉浸式画板 ---
st.set_page_config(page_title="Haval Visual Lab", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #05070a; color: white; }
    /* 左侧控制台 */
    section[data-testid="stSidebar"] { background-color: #0e1117 !important; border-right: 1px solid #333; width: 420px !important; }
    /* 幻灯片画板 */
    .slide-canvas {
        background: white; border-radius: 20px; padding: 0; overflow: hidden;
        box-shadow: 0 30px 60px rgba(0,0,0,0.5); min-height: 560px; color: #333;
        display: flex; flex-direction: column;
    }
    .slide-text { padding: 40px; flex: 1; }
    .kv-placeholder { height: 350px; background: #1a1a1a; display: flex; align-items: center; justify-content: center; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：创意执行台 ---
with st.sidebar:
    st.title("🦔 Nano Visual Lab")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    st.markdown("---")
    user_cmd = st.chat_input("说出你的哈弗竞标想法...")
    
    # 核心按钮区
    st.write("🛠️ **生产力工具**")
    if st.button("📝 生成/更新文案 (Flash)", use_container_width=True):
        if user_cmd:
            model = genai.GenerativeModel('gemini-2.5-flash')
            res = model.generate_content(f"你是哈弗公关总监。根据需求'{user_cmd}'，写出PPT页面的核心内容。")
            st.session_state.ppt_content = res.text
            st.rerun()

    if st.button("🖼️ 生成竞标级 KV (Imagen 3)", use_container_width=True):
        with st.spinner("正在调用 Imagen 3.0 绘制顶奢 KV..."):
            try:
                # 只有这里才会调用昂贵的绘图模型
                img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                # 自动根据文案生成 Prompt
                img_prompt = f"A professional high-end Key Visual for Haval Raptor (哈弗猛龙) SUV, cinematic lighting, hardcore off-road style, mountains background, photorealistic, 4k."
                res = img_model.generate_images(prompt=img_prompt, number_of_images=1)
                st.session_state.kv_image = res.images[0]
                st.rerun()
            except Exception as e:
                st.error(f"绘图引擎需在 Google Cloud 开启: {e}")

# --- 4. 右侧：沉浸式幻灯片预览 ---
st.subheader("PPT 页面效果预览")

with st.container():
    st.markdown('<div class="slide-canvas">', unsafe_allow_html=True)
    
    # 视觉区域 (KV图)
    if st.session_state.kv_image:
        st.image(st.session_state.kv_image, use_container_width=True)
    else:
        st.markdown('<div class="kv-placeholder">🖼️ 点击左侧“生成 KV”即可实时绘图</div>', unsafe_allow_html=True)
    
    # 文案区域
    st.markdown('<div class="slide-text">', unsafe_allow_html=True)
    st.markdown(st.session_state.ppt_content)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# 底部：深度润色
if st.button("✨ 深度润色文案 (3.1 Pro)"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    res = pro.generate_content(f"用犀利的公关措辞润色：{st.session_state.ppt_content}")
    st.session_state.ppt_content = res.text
    st.rerun()
