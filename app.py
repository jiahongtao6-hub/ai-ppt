import streamlit as st
import google.generativeai as genai

# --- 1. 动力系统 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 2. 核心状态锁 (单向闯关，不用 Radio) ---
if 'step_level' not in st.session_state: st.session_state.step_level = 1 # 1:大纲, 2:内容填充
if 'history' not in st.session_state: st.session_state.history = []
if 'outline' not in st.session_state: st.session_state.outline = ""
if 'content' not in st.session_state: st.session_state.content = ""
if 'kv' not in st.session_state: st.session_state.kv = None

# --- 3. 界面重塑 ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 420px !important; }
    .status-bar { padding: 10px; background: #1a1a1a; color: #fff; font-weight: bold; border-radius: 8px; margin-bottom: 20px; text-align: center; }
    .anchor-box { background: #fff3e6; border-left: 4px solid #ff6b00; padding: 15px; border-radius: 4px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption("🚀 Paid Tier 3 | 余额: HK$2,340")
    
    st.markdown("---")
    # 显示当前闯关进度
    if st.session_state.step_level == 1:
        st.success("📍 当前阶段：1. 大纲构思")
    else:
        st.success("📍 当前阶段：2. 内容与视觉执行")
        if st.button("↩️ 返回修改大纲", use_container_width=True):
            st.session_state.step_level = 1
            st.rerun()

    chat_box = st.container(height=350)
    for m in st.session_state.history:
        chat_box.chat_message(m["role"]).write(m["content"])

    if user_cmd := st.chat_input("对我下达指令..."):
        st.session_state.history.append({"role": "user", "content": user_cmd})
        with st.spinner("极速响应中..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 根据进度切换大脑逻辑
            if st.session_state.step_level == 1:
                sys_prompt = "你是哈弗公关总监。禁止 emoji。直接根据用户需求输出结构化的 PPT 大纲。"
                res = model.generate_content(f"{sys_prompt}\n指令：{user_cmd}")
                st.session_state.outline = res.text
            else:
                sys_prompt = f"你是视觉设计总监。必须严格基于以下大纲行事：\n{st.session_state.outline}\n规则：禁止 emoji。输出本页的核心文案、Hex配色、排版建议。"
                res = model.generate_content(f"{sys_prompt}\n指令：{user_cmd}")
                st.session_state.content = res.text
            
            st.session_state.history.append({"role": "assistant", "content": "✅ 已更新，请看右侧。"})
            st.rerun()

    st.markdown("---")
    if st.button("🗑️ 清空重来", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- 4. 右侧画板 ---
if st.session_state.step_level == 1:
    st.markdown('<div class="status-bar">🎯 阶段一：打磨传播大纲</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(st.session_state.outline if st.session_state.outline else "👈 在左侧输入你的哈弗猛龙传播方向，生成大纲。")
    
    # 闯关按钮
    if st.session_state.outline:
        if st.button("✅ 大纲确认无误，进入详细内容填充 ➡️", type="primary"):
            st.session_state.step_level = 2
            st.rerun()

elif st.session_state.step_level == 2:
    st.markdown('<div class="status-bar">🎯 阶段二：设计与文案执行</div>', unsafe_allow_html=True)
    
    # 顶部锁定大纲锚点
    st.markdown("📜 **锁定的大纲锚点**")
    st.markdown(f'<div class="anchor-box">{st.session_state.outline}</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.5, 1])
    with col1:
        st.write("🖼️ **16:9 视觉预览**")
        if st.session_state.kv:
            st.image(st.session_state.kv, use_container_width=True)
        else:
            st.markdown('<div style="aspect-ratio:16/9; background:#eee; display:flex; align-items:center; justify-content:center; border-radius:8px;">点击下方按钮生成商业级 KV</div>', unsafe_allow_html=True)
        
        if st.button("🖼️ 生成 Imagen 4.0 顶奢 KV"):
            with st.spinner("绘图中..."):
                try:
                    v_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                    v_res = v_model.generate_content(f"High-end PR KV for Haval Raptor SUV based on: {st.session_state.content}")
                    if v_res.candidates[0].content.parts[0].inline_data:
                        st.session_state.kv = v_res.candidates[0].content.parts[0].inline_data.data
                        st.rerun()
                except Exception as e: st.error(f"异常: {e}")

    with col2:
        st.write("📝 **设计与文案 Spec**")
        with st.container(border=True):
            st.markdown(st.session_state.content if st.session_state.content else "👈 在左侧输入要求，生成本页详情。")
