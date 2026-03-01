import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 动力系统：锁定 2026 顶级模型 (Tier 3) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 【核心精简】：砍掉 diagnosis，直接从大纲起步
for key in ['step', 'history', 'outline', 'content', 'kv']:
    if key not in st.session_state:
        if key == 'step': st.session_state[key] = "大纲构思"
        elif key == 'history': st.session_state[key] = []
        elif key == 'kv': st.session_state[key] = None
        else: st.session_state[key] = ""

# --- 2. 界面审美：Nano Studio 纯净画板 ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 420px !important; }
    .slide-canvas {
        background: white; border-radius: 12px; padding: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); border: 1px solid #ddd;
        min-height: 500px; color: #333;
    }
    .status-badge { padding: 5px 12px; border-radius: 20px; background: #fff3e6; color: #ff6b00; font-weight: bold; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通 (纯执行总监人格) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 砍掉策略诊断，只有三个硬核执行环节
    steps = ["大纲构思", "内容填充", "视觉定稿"]
    st.radio("🎯 当前执行阶段", steps, key="step")
    
    chat_box = st.container(height=380)
    for m in st.session_state.history:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_cmd := st.chat_input("输入哈弗方案想法，直接出大纲..."):
        st.session_state.history.append({"role": "user", "content": user_cmd})
        with st.spinner(f"正在极速生成：{st.session_state.step}"):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 【强制约束】：禁止反问，直接输出
            sys_prompt = f"""
            你是一位高效的公关视觉设计总监。
            当前环节：【{st.session_state.step}】。
            已锁死大纲锚点：{st.session_state.outline}
            
            规则：
            1. 严禁反问用户！严禁分析策略合理性！直接执行输出。
            2. 禁止使用 emoji。
            3. 如果处于【大纲构思】，直接输出结构化的 PPT 大纲。
            4. 如果处于【内容填充】，基于大纲直接输出：核心文案、Hex 色值、排版说明。
            """
            
            res = model.generate_content(f"{sys_prompt}\n最新指令：{user_cmd}")
            
            if st.session_state.step == "大纲构思": st.session_state.outline = res.text
            elif st.session_state.step == "内容填充": st.session_state.content = res.text
            
            st.session_state.history.append({"role": "assistant", "content": f"✅ {st.session_state.step}已更新，请在右侧查阅。"})
            st.rerun()

# --- 4. 右侧：直接输出预览 ---
st.markdown(f'<span class="status-badge">📍 当前进度：{st.session_state.step}</span>', unsafe_allow_html=True)

col_view, col_anchor = st.columns([1.2, 1])

with col_view:
    st.write("🖼️ **执行画板**")
    if st.session_state.kv:
        st.image(st.session_state.kv, use_container_width=True)
    
    with st.container(border=True):
        content_to_show = st.session_state.content if st.session_state.step == "内容填充" else st.session_state.outline
        st.markdown(content_to_show if content_to_show else "等待输入直接生成...")

with col_anchor:
    st.write("📜 **大纲锚点 (Anchor)**")
    with st.container(border=True):
        st.markdown(st.session_state.outline if st.session_state.outline else "等待大纲生成...")

# 底部工具区
st.sidebar.markdown("---")
if st.sidebar.button("🖼️ 生成 Imagen 4.0 顶奢 KV"):
