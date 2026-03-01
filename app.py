import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 动力系统：锁定 2026 顶级模型 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化状态：增加“已确认大纲”锚点
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'ppt_data' not in st.session_state: 
    st.session_state.ppt_data = {"diagnosis": "", "outline": "", "content": "", "kv": None}
if 'stage' not in st.session_state: st.session_state.stage = "策略诊断"

# --- 2. 界面设计 ---
st.set_page_config(page_title="Nano Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 450px !important; }
    .stage-card { background: #fff3e6; padding: 12px; border-radius: 8px; border-left: 5px solid #ff6b00; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通 (视觉总监人格 + 逻辑锚点) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 显式阶段选择：增加 Key 确保状态不丢失
    current_stage = st.radio("🎯 任务锁定", ["策略诊断", "大纲构思", "内容填充", "视觉定稿"], key="stage_radio")
    st.session_state.stage = current_stage
    
    chat_box = st.container(height=380)
    for m in st.session_state.chat_log:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_cmd := st.chat_input("下达指令..."):
        st.session_state.chat_log.append({"role": "user", "content": user_cmd})
        with st.spinner(f"正在推进：{st.session_state.stage}"):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 【核心优化】：将已生成的大纲作为硬核背景强制塞入 Prompt
            context_outline = st.session_state.ppt_data['outline']
            
            # 引入 NanoBanana 风格的严格约束
            sys_prompt = f"""
            你是一位哈弗公关视觉设计总监。
            当前阶段：【{st.session_state.stage}】。
            已确认的大纲如下（严禁偏离）：
            {context_outline}
            
            规则：
            1. 必须基于已确认的大纲内容向下推进，禁止跳回或重新生成大纲。
            2. 使用专业、犀利的公关语调。
            3. 禁止使用 emoji。
            """
            
            res = model.generate_content(f"{sys_prompt}\n最新指令：{user_cmd}")
            
            # 更新对应数据
            if st.session_state.stage == "策略诊断": st.session_state.ppt_data["diagnosis"] = res.text
            elif st.session_state.stage == "大纲构思": st.session_state.ppt_data["outline"] = res.text
            elif st.session_state.stage == "内容填充": st.session_state.ppt_data["content"] = res.text
            
            st.session_state.chat_log.append({"role": "assistant", "content": f"✅ {st.session_state.stage}已同步至画板。"})
            st.rerun()

# --- 4. 右侧：全案画板 (即看即所得) ---
st.markdown(f'<div class="stage-card">📍 当前环节：{st.session_state.stage}</div>', unsafe_allow_html=True)

col_out, col_con = st.columns([1, 1.2])

with col_out:
    st.subheader("大纲架构 (Anchor)")
    with st.container(border=True):
        st.markdown(st.session_state.ppt_data["outline"] if st.session_state.ppt_data["outline"] else "等待大纲生成...")

with col_con:
    st.subheader("深度公关文案 (Execution)")
    with st.container(border=True):
        st.markdown(st.session_state.ppt_data["content"] if st.session_state.ppt_data["content"] else "等待填充内容...")

# 视觉定稿
if st.session_state.stage == "视觉定稿" or st.session_state.ppt_data["content"]:
    st.markdown("---")
    if st.button("🖼️ 生成 Imagen 4.0 商业级 KV"):
        with st.spinner("视觉总监正在根据成稿绘图..."):
            try:
                v_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                v_res = v_model.generate_content(f"A high-end PR KV for Haval Raptor SUV based on: {st.session_state.ppt_data['content']}")
                if v_res.candidates[0].content.parts[0].inline_data:
                    st.session_state.ppt_data["kv"] = v_res.candidates[0].content.parts[0].inline_data.data
            except Exception as e: st.error(f"视觉引擎连接中: {e}")

    if st.session_state.ppt_data["kv"]:
        st.image(st.session_state.ppt_data["kv"], caption="策略驱动的视觉预览", use_container_width=True)

# 工具箱
st.sidebar.markdown("---")
if st.sidebar.button("🗑️ 重置全案记忆"):
    st.session_state.clear()
    st.rerun()
