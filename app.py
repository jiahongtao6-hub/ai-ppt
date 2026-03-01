import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 动力系统：锁定 2026 顶级模型 (Tier 3) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 【核心修复：KeyError 保护锁】确保所有柜子在开门前都有东西
for key in ['step', 'history', 'diagnosis', 'outline', 'content', 'kv']:
    if key not in st.session_state:
        if key == 'step': st.session_state[key] = "策略诊断"
        elif key == 'history': st.session_state[key] = []
        elif key == 'kv': st.session_state[key] = None
        else: st.session_state[key] = ""

# --- 2. 界面审美：对标 Nano Studio 纯净画板 ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 420px !important; }
    /* PPT 预览卡片 */
    .slide-canvas {
        background: white; border-radius: 12px; padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); border: 1px solid #ddd;
        min-height: 500px; color: #333;
    }
    .status-badge { padding: 5px 12px; border-radius: 20px; background: #fff3e6; color: #ff6b00; font-weight: bold; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通 (视觉设计总监人格) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 环节锁定 (通过 index 确保状态同步)
    steps = ["策略诊断", "大纲构思", "内容填充", "视觉定稿"]
    st.radio("🎯 当前执行阶段", steps, key="step")
    
    chat_box = st.container(height=380)
    for m in st.session_state.history:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_cmd := st.chat_input("对我下达哈弗竞标指令..."):
        st.session_state.history.append({"role": "user", "content": user_cmd})
        with st.spinner(f"正在推进：{st.session_state.step}"):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 植入 NanoBanana 的商业级灵魂
            sys_prompt = f"""
            你是一位融合战略思维与顶级设计美学的视觉设计总监。
            当前环节：【{st.session_state.step}】。
            逻辑上下文：{st.session_state.outline}
            
            规则：
            1. 禁止使用 emoji。
            2. 如果处于【策略诊断】，先评估用户传播方向的杀伤力。
            3. 如果处于【内容填充】，输出包含：核心逻辑、视觉策略、Hex 色值、排版建议。
            """
            
            res = model.generate_content(f"{sys_prompt}\n最新指令：{user_cmd}")
            
            # 数据安全写入
            if st.session_state.step == "策略诊断": st.session_state.diagnosis = res.text
            elif st.session_state.step == "大纲构思": st.session_state.outline = res.text
            elif st.session_state.step == "内容填充": st.session_state.content = res.text
            
            st.session_state.history.append({"role": "assistant", "content": f"✅ {st.session_state.step}已更新。"})
            st.rerun()

# --- 4. 右侧：全案预览与设计指南 ---
st.markdown(f'<span class="status-badge">📍 当前进度：{st.session_state.step}</span>', unsafe_allow_html=True)

col_view, col_spec = st.columns([1.2, 1])

with col_view:
    st.write("🖼️ **视觉成稿预览**")
    if st.session_state.kv:
        st.image(st.session_state.kv, use_container_width=True)
    
    with st.container(border=True):
        # 修复空白问题：直接渲染 Markdown
        content_to_show = st.session_state.content if st.session_state.step == "内容填充" else st.session_state.outline
        st.markdown(content_to_show if content_to_show else "等待方案生成...")

with col_spec:
    st.write("📜 **设计执行策略 (Spec Sheet)**")
    with st.container(border=True):
        st.markdown(st.session_state.diagnosis if st.session_state.diagnosis else "等待输入传播想法...")

# 工具区
st.sidebar.markdown("---")
if st.sidebar.button("🖼️ 生成 Imagen 4.0 顶奢 KV"):
    with st.spinner("视觉总监构图中..."):
        try:
            v_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
            v_res = v_model.generate_content(f"High-end PR KV for Haval Raptor SUV based on: {st.session_state.content}")
            if v_res.candidates[0].content.parts[0].inline_data:
                st.session_state.kv = v_res.candidates[0].content.parts[0].inline_data.data
                st.rerun()
        except Exception as e: st.error(f"视觉引擎连接中: {e}")

if st.sidebar.button("✨ 3.1 Pro 深度润色"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    st.session_state.content = pro.generate_content(f"专业润色：{st.session_state.content}").text
    st.rerun()
