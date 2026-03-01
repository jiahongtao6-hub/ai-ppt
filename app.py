import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 核心动力：锁定 2026 顶级模型路径 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 初始化：记录策略逻辑与全案进度
if 'chat_log' not in st.session_state: st.session_state.chat_log = []
if 'strategy_board' not in st.session_state: 
    st.session_state.strategy_board = {"diagnosis": "", "outline": "", "content": "", "kv": None}
if 'work_phase' not in st.session_state: st.session_state.work_phase = "策略诊断"

# --- 2. 极致审美：Nano Studio 专业视觉规范 ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #fcfcfc; color: #1a1a1a; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 450px !important; }
    /* 策略画板容器 */
    .strategy-card {
        background: white; border-radius: 12px; padding: 35px; margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03); border: 1px solid #f0f0f0;
    }
    .phase-tag { color: #ff6b00; font-weight: bold; font-size: 0.9rem; margin-bottom: 15px; }
    .stButton>button { border-radius: 8px; font-weight: 500; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：深度沟通区 (战略咨询 + 视觉总监) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 强制分步流控制
    st.session_state.work_phase = st.radio("当前工作流", ["策略诊断", "大纲架构", "内容填充", "视觉定稿"])
    
    chat_box = st.container(height=380)
    for m in st.session_state.chat_log:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_idea := st.chat_input("输入你的传播想法或指令..."):
        st.session_state.chat_log.append({"role": "user", "content": user_idea})
        with st.spinner(f"正在进行{st.session_state.work_phase}..."):
            # 锁定 2.5-flash 引擎保证沟通无延迟
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 注入专业公关策略提示词
            sys_prompt = f"""
            你是一位顶尖公关战略顾问。当前阶段：【{st.session_state.work_phase}】。
            任务：针对哈弗(Haval)竞标案。
            逻辑：严禁使用 emoji。必须先评估传播方向的合理性、差异化和竞品杀伤力，再输出对应内容。
            """
            
            res = model.generate_content(f"{sys_prompt}\n用户想法：{user_idea}")
            
            # 状态同步
            if st.session_state.work_phase == "策略诊断": st.session_state.strategy_board["diagnosis"] = res.text
            elif st.session_state.work_phase == "大纲架构": st.session_state.strategy_board["outline"] = res.text
            elif st.session_state.work_phase == "内容填充": st.session_state.strategy_board["content"] = res.text
            
            st.session_state.chat_log.append({"role": "assistant", "content": f"已完成{st.session_state.work_phase}，请查阅右侧。"})
            st.rerun()

# --- 4. 右侧：实时策略与画板同步 ---
st.subheader("哈弗（Haval）竞标全案：实时预览画板")

col_main, col_sub = st.columns([1, 1])

with col_main:
    st.markdown('<div class="phase-tag">📍 策略诊断与逻辑</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(st.session_state.strategy_board["diagnosis"] if st.session_state.strategy_board["diagnosis"] else "等待输入传播想法...")

with col_sub:
    st.markdown('<div class="phase-tag">📜 大纲与内容</div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(st.session_state.strategy_board["outline"] if st.session_state.strategy_board["outline"] else "策略定稿后生成大纲...")

# 底部：视觉与生产力
st.markdown("---")
b1, b2, b3, _ = st.columns([1.5, 1, 1, 2])

with b1:
    if st.button("🖼️ 确认策略，生成 Imagen 4.0 视觉 KV"):
        with st.spinner("视觉总监正在根据策略构图..."):
            try:
                # 锁定顶级 Imagen 4.0
                v_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                v_res = v_model.generate_content(f"A high-end PR Key Visual for Haval Raptor SUV based on strategy: {st.session_state.strategy_board['diagnosis']}")
                if v_res.candidates[0].content.parts[0].inline_data:
                    st.session_state.strategy_board["kv"] = v_res.candidates[0].content.parts[0].inline_data.data
            except Exception as e: st.error(f"视觉引擎连接中: {e}")

if st.session_state.strategy_board["kv"]:
    st.image(st.session_state.strategy_board["kv"], caption="基于策略生成的视觉成稿", use_container_width=True)

if b2.button("✨ 3.1 Pro 深度润色"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    st.session_state.strategy_board["content"] = pro.generate_content(f"专业润色内容：{st.session_state.strategy_board['content']}").text
    st.rerun()

b3.download_button("📥 导出 PPTX 定稿", data="...", file_name="Haval_Proposal.pptx")
