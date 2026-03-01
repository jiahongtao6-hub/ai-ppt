import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 配置 2026 顶级动力 (锁定你的 Tier 3 权限) ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 核心状态管理：锁定全生命周期
if 'history' not in st.session_state: st.session_state.chat_history = []
if 'ppt_data' not in st.session_state: 
    st.session_state.ppt_data = {"diagnosis": "", "outline": "", "current_page": "", "design_spec": "", "kv": None}
if 'step' not in st.session_state: st.session_state.step = "策略诊断"

# --- 2. 审美重塑：沉浸式 16:9 画板 UI ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    /* 左侧对话面板 */
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 450px !important; }
    /* 16:9 幻灯片画布 */
    .slide-canvas {
        width: 100%; aspect-ratio: 16/9; background: white; border-radius: 12px;
        box-shadow: 0 20px 50px rgba(0,0,0,0.08); border: 1px solid #ddd;
        position: relative; overflow: hidden; display: flex; flex-direction: column;
    }
    .spec-sheet { background: #fdfdfd; padding: 20px; border-top: 1px solid #eee; font-family: monospace; font-size: 0.8rem; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通台 (视觉总监人格) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 强制环节控制
    st.session_state.step = st.radio("当前任务目标", ["策略诊断", "大纲构思", "内容填充", "视觉定稿"], 
                                     index=["策略诊断", "大纲构思", "内容填充", "视觉定稿"].index(st.session_state.step))
    
    chat_box = st.container(height=350)
    for m in st.session_state.chat_history:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_cmd := st.chat_input("对我下达哈弗竞标指令..."):
        st.session_state.chat_history.append({"role": "user", "content": user_cmd})
        with st.spinner(f"正在推进：{st.session_state.step}"):
            # 锁定 2.5 Flash 保证沟通速度
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 【核心逻辑】：将 NanoBanana 的工作流注入每一轮对话
            sys_prompt = f"""
            你是一位融合咨询公司战略思维与国际一线品牌美学的视觉设计总监。
            当前阶段：【{st.session_state.step}】。
            已定稿大纲：{st.session_state.ppt_data['outline']}
            
            任务：
            1. 禁止使用 emoji。
            2. 严禁回退阶段。如果用户确认大纲，必须开始详细页面设计。
            3. 输出内容必须包含：核心逻辑、设计执行策略、色彩方案(Hex)、版面结构。
            """
            
            res = model.generate_content(f"{sys_prompt}\n最新指令：{user_cmd}")
            
            # 数据落盘
            if st.session_state.step == "策略诊断": st.session_state.ppt_data["diagnosis"] = res.text
            elif st.session_state.step == "大纲构思": st.session_state.ppt_data["outline"] = res.text
            elif st.session_state.step == "内容填充": st.session_state.ppt_data["current_page"] = res.text
            
            st.session_state.chat_history.append({"role": "assistant", "content": "已完成当前页设计，请查看右侧画板。"})
            st.rerun()

# --- 4. 右侧：沉浸式幻灯片画板 ---
st.subheader("哈弗（Haval）竞标案：实时预览画板")

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.write("🖼️ **当前 Slide 视觉预览**")
    with st.container():
        st.markdown('<div class="slide-canvas">', unsafe_allow_html=True)
        
        # 视觉核心：Imagen 4.0 绘图
        if st.session_state.ppt_data["kv"]:
            st.image(st.session_state.ppt_data["kv"], use_container_width=True)
        else:
            st.markdown('<div style="height:100%; display:flex; align-items:center; justify-content:center; color:#999;">等待生成视觉 KV 或投喂参考图</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.write("📜 **设计执行方案 (Spec Sheet)**")
    with st.container():
        st.markdown('<div class="spec-sheet">', unsafe_allow_html=True)
        st.markdown(st.session_state.ppt_data["current_page"] if st.session_state.ppt_data["current_page"] else "等待设计方案输出...")
        st.markdown('</div>', unsafe_allow_html=True)

# 底部：生产力工具
st.markdown("---")
b1, b2, b3, _ = st.columns([1.5, 1, 1, 3])
with b1:
    if st.button("🖼️ 基于方案生成 Imagen 4.0 商业级 KV"):
        with st.spinner("绘图引擎启动中..."):
            try:
                img_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                img_res = img_model.generate_content(f"A professional PR Key Visual for Haval Raptor SUV, cinematic lighting, based on: {st.session_state.ppt_data['current_page']}")
                if img_res.candidates[0].content.parts[0].inline_data:
                    st.session_state.ppt_data["kv"] = img_res.candidates[0].content.parts[0].inline_data.data
                    st.rerun()
            except Exception as e: st.error(f"视觉接口异常: {e}")

if b2.button("✨ 3.1 Pro 深度润色"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    st.session_state.ppt_data["current_page"] = pro.generate_content(f"用犀利的公关语气润色：{st.session_state.ppt_data['current_page']}").text
    st.rerun()

b3.download_button("📥 导出 PPTX 定稿", data="...", file_name="Haval_Proposal.pptx")
