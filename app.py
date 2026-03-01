import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. 动力系统：锁定 2026 顶级模型 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# 【初始化核心】：确保所有“柜子”在开门前都有东西
if 'step' not in st.session_state: st.session_state.step = "策略诊断"
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'ppt_data' not in st.session_state: 
    st.session_state.ppt_data = {
        "diagnosis": "等待输入想法...", 
        "outline": "等待生成大纲...", 
        "current_page": "等待设计执行方案...", 
        "kv": None
    }

# --- 2. 界面设计：沉浸式 16:9 画板 ---
st.set_page_config(page_title="Haval Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 420px !important; }
    /* 16:9 画布容器 */
    .slide-canvas {
        width: 100%; aspect-ratio: 16/9; background: white; border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.05); border: 1px solid #ddd;
        position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
    }
    .spec-sheet { background: #fdfdfd; padding: 25px; border-radius: 10px; border: 1px solid #eee; font-family: monospace; font-size: 0.85rem; line-height: 1.6; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 左侧：交互沟通台 (视觉总监人格) ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption(f"🚀 Paid Tier 3 | 余额: HK$2,340")
    
    # 使用 key 直接同步，彻底告别 KeyError
    st.radio("🎯 当前执行阶段", 
             ["策略诊断", "大纲构思", "内容填充", "视觉定稿"], 
             key="step")
    
    chat_box = st.container(height=380)
    for m in st.session_state.chat_history:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    if user_cmd := st.chat_input("下达哈弗竞标指令..."):
        st.session_state.chat_history.append({"role": "user", "content": user_cmd})
        with st.spinner(f"正在推进：{st.session_state.step}"):
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # 注入 NanoBanana 核心提示词与哈弗品牌逻辑
            sys_prompt = f"""
            你是一位顶尖公关战略顾问与视觉设计总监。
            任务：为哈弗(Haval)竞标案提供支持。
            当前环节：【{st.session_state.step}】。
            定稿参考：{st.session_state.ppt_data['outline']}
            
            规则：
            1. 严禁使用 emoji。
            2. 严禁回跳。如果处于【内容填充】，必须基于大纲生成详细的“页面设计执行方案”。
            3. 输出包含：核心逻辑、视觉策略、色彩方案(Hex)、版面结构建议。
            """
            
            res = model.generate_content(f"{sys_prompt}\n指令：{user_cmd}")
            
            # 数据安全写入，防止 Key 错误
            if st.session_state.step == "策略诊断": st.session_state.ppt_data["diagnosis"] = res.text
            elif st.session_state.step == "大纲构思": st.session_state.ppt_data["outline"] = res.text
            elif st.session_state.step == "内容填充": st.session_state.ppt_data["current_page"] = res.text
            
            st.session_state.chat_history.append({"role": "assistant", "content": f"✅ {st.session_state.step}已更新。"})
            st.rerun()

# --- 4. 右侧：沉浸式预览与 Spec Sheet ---
st.subheader("哈弗竞标方案：可视化画板")

c_left, c_right = st.columns([1.5, 1])

with c_left:
    st.write("🖼️ **16:9 视觉画板预览**")
    with st.container():
        st.markdown('<div class="slide-canvas">', unsafe_allow_html=True)
        if st.session_state.ppt_data.get("kv"):
            st.image(st.session_state.ppt_data["kv"], use_container_width=True)
        else:
            st.write("🖼️ 待生成或投喂视觉 KV")
        st.markdown('</div>', unsafe_allow_html=True)

with c_right:
    st.write("📜 **设计执行方案 (Spec Sheet)**")
    # 动态显示当前阶段内容
    display_content = st.session_state.ppt_data["current_page"] if st.session_state.step == "内容填充" else st.session_state.ppt_data["outline"]
    st.markdown(f'<div class="spec-sheet">{display_content}</div>', unsafe_allow_html=True)

# 底部生产力工具
st.markdown("---")
col_b1, col_b2, col_b3, _ = st.columns([1.5, 1, 1, 3])

with col_b1:
    if st.button("🖼️ 生成 Imagen 4.0 商业级 KV"):
        with st.spinner("视觉总监构图中..."):
            try:
                v_model = genai.GenerativeModel('imagen-4.0-ultra-generate-001')
                v_res = v_model.generate_content(f"High-end PR KV for Haval Raptor SUV, cinematic lighting, professional photography, based on: {st.session_state.ppt_data['current_page']}")
                if v_res.candidates[0].content.parts[0].inline_data:
                    st.session_state.ppt_data["kv"] = v_res.candidates[0].content.parts[0].inline_data.data
                    st.rerun()
            except Exception as e: st.error(f"视觉引擎连接中: {e}")

if col_b2.button("✨ 3.1 Pro 深度润色"):
    pro = genai.GenerativeModel('gemini-3.1-pro-preview')
    st.session_state.ppt_data["current_page"] = pro.generate_content(f"专业润色哈弗方案：{st.session_state.ppt_data['current_page']}").text
    st.rerun()

col_b3.download_button("📥 导出 PPTX 定稿", data="...", file_name="Haval_Proposal.pptx")
