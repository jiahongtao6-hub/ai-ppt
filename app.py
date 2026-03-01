import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：顶级视觉设计总监人格注入 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 状态管理：锁定全生命周期
if 'history' not in st.session_state: st.session_state.history = []
if 'current_slide' not in st.session_state: 
    st.session_state.current_slide = {"title": "哈弗猛龙：智电越野", "content": "等待策略注入...", "design_specs": {}, "kv": None}
if 'vibe' not in st.session_state: st.session_state.vibe = "未定义"

# --- 2. 极致审美：Nano Studio 纯净视觉规范 ---
st.set_page_config(page_title="Nano Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #1a1a1a; }
    /* 左侧对话面板 */
    section[data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #eee; width: 420px !important; }
    /* 商业级幻灯片画板 */
    .slide-canvas {
        background: white; border-radius: 12px; border: 1px solid #efefef;
        box-shadow: 0 10px 40px rgba(0,0,0,0.04); min-height: 550px;
        position: relative; overflow: hidden;
    }
    .design-specs { background: #f8f9fa; border-top: 1px solid #eee; padding: 20px; font-size: 0.85rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通台 (视觉总监人格) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption("🚀 Paid Tier 3 | 余额: HK$2,340")
    
    chat_container = st.container(height=350)
    for m in st.session_state.history:
        chat_container.chat_message(m["role"]).write(m["content"])
    
    # 风格库：支持点选、复刻与投喂
    st.markdown("---")
    st.write("🎨 **风格与审美投喂**")
    uploaded_style = st.file_uploader("🖼️ 投喂审美参考 (可选)", type=['png', 'jpg'])
    
    if user_cmd := st.chat_input("对我下达哈弗竞标指令..."):
        st.session_state.history.append({"role": "user", "content": user_cmd})
        with st.spinner("视觉设计总监正在思考..."):
            # 锁定 2.5 Flash 保证快速迭代
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 注入“别人家”的核心提示词逻辑
            system_prompt = """
            你是一位融合咨询公司战略思维与一线设计美学的视觉设计总监。
            任务：为哈弗(Haval)竞标案生成 PPT 方案。
            规则：禁止使用 emoji。每一页需输出：标题、内容逻辑、设计执行策略（含色值、版面结构）。
            """
            
            if uploaded_style:
                res = model.generate_content([system_prompt, user_cmd, Image.open(uploaded_style)])
            else:
                res = model.generate_content(f"{system_prompt}\n指令：{user_cmd}")
            
            st.session_state.current_slide["content"] = res.text
            st.session_state.history.append({"role": "assistant", "content": "设计方案已在右侧生成。"})
            st.rerun()

# --- 4. 右侧：全案视觉画板 ---
st.subheader("生成的视觉成稿预览")

with st.container():
    st.markdown('<div class="slide-canvas">', unsafe_allow_html=True)
    
    # 上半部分：视觉 KV
    if st.button("🖼️ 生成 Imagen 4.0 顶奢视觉"):
        with st.spinner("正在绘制竞标级大片..."):
            try:
                img_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                img_res = img_model.generate_content(f"High-end PR Key Visual for Haval Raptor SUV, based on professional design specs: {st.session_state.current_slide['content']}")
                if img_res.candidates[0].content.parts[0].inline_data:
                    st.session_state.current_slide["kv"] = img_res.candidates[0].content.parts[0].inline_data.data
            except Exception as e: st.error(f"视觉引擎连接中: {e}")

    if st.session_state.current_slide["kv"]:
        st.image(st.session_state.current_slide["kv"], use_container_width=True)
    else:
        st.markdown('<div style="height:350px; background:#f0f0f0; display:flex; align-items:center; justify-content:center;">🖼️ 待生成视觉 KV</div>', unsafe_allow_html=True)
    
    # 下半部分：文案与设计规格
    st.markdown('<div class="design-specs">', unsafe_allow_html=True)
    st.markdown(st.session_state.current_slide["content"])
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# 底部生产力工具
st.markdown("---")
b1, b2, b3, _ = st.columns([1, 1, 1, 3])
if b1.button("✨ 3.1 Pro 深度润色"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    st.session_state.current_slide["content"] = pro.generate_content(f"专业润色哈弗竞标文案：{st.session_state.current_slide['content']}").text
    st.rerun()

b2.button("👁️ 全屏演示", use_container_width=True)
b3.download_button("📥 导出 PPTX 定稿", data="...", file_name="Haval_Raptor.pptx")
