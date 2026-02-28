import streamlit as st
import google.generativeai as genai
import os

# --- 1. 核心安全配置：强制锁定 v1 正式版，杜绝 404 报错 ---
os.environ["GOOGLE_API_VERSION"] = "v1" 

# 从 Streamlit 的 Secrets 中读取 Key，既安全又不报错
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
else:
    st.error("请先在 Streamlit 后台设置中配置你的 API Key")

# --- 2. 高审美 CSS (仿 Nano Studio 风格) ---
st.set_page_config(page_title="哈弗猛龙 PR 实验室", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    }
    .stButton>button { background-color: #ff6b00; color: white; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 3. 界面逻辑 ---
st.title("🚗 哈弗（Haval）竞标策略中心")
st.caption("当前权限：Paid Tier 3 (Unlimited)")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown("### 1. 风格选择")
    st.markdown('<div class="card">🔥 硬核越野 | ⚡ 智电科技</div>', unsafe_allow_html=True)
    
    st.markdown("### 2. 输入需求")
    prompt = st.text_area("输入竞标核心点：", placeholder="例如：哈弗猛龙对比山海 T2 的公关策略...")
    
    if st.button("🚀 生成方案"):
        # 调用逻辑最强的 Pro 模型
        model = genai.GenerativeModel('gemini-1.5-pro')
        response = model.generate_content(f"作为哈弗公关专家，请针对以下内容写出 PPT 大纲：{prompt}")
        st.session_state.result = response.text

with col2:
    st.markdown("### 🖼️ 预览区")
    if 'result' in st.session_state:
        st.text_area("方案详情：", value=st.session_state.result, height=500)
    else:
        st.info("方案生成后将显示在这里。")