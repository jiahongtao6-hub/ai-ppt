import streamlit as st
import google.generativeai as genai

# 1. 强制锁定 v1 正式版（Tier 3 专属通道）
import os
os.environ["GOOGLE_API_VERSION"] = "v1"

# 2. 读取 Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())
else:
    st.error("🔑 没找到 API Key，请检查 Settings -> Secrets")
    st.stop()

# 3. 高审美 UI (哈弗猛龙定制版)
st.set_page_config(page_title="哈弗 PR 实验室", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card { background: rgba(255,255,255,0.05); border-radius: 12px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .stButton>button { background-color: #ff6b00; color: white; width: 100%; border: none; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 哈弗（Haval）竞标策略中心")
left, right = st.columns([1, 1.5])

with left:
    st.markdown("### 1. 风格选择")
    st.markdown('<div class="card">🔥 硬核越野 | ⚡ 智电科技</div>', unsafe_allow_html=True)
    
    prompt = st.text_area("输入你的哈弗竞标需求：", placeholder="例如：哈弗猛龙 2026 年度公关传播方案大纲...")
    
    if st.button("🚀 生成方案"):
        if not prompt.strip():
            st.warning("请先输入需求内容哦！")
        else:
            with st.spinner("正在调用 Paid Tier 3 顶级逻辑..."):
                try:
                    # 【核心修正】：去掉 models/ 前缀，直接使用模型名
                    model = genai.GenerativeModel('gemini-1.5-pro') 
                    response = model.generate_content(f"作为哈弗公关专家，请写出 PPT 大纲：{prompt}")
                    st.session_state.result = response.text
                except Exception as e:
                    st.error(f"生成时遇到小问题：{e}")

with right:
    st.markdown("### 🖼️ PPT 方案预览")
    if 'result' in st.session_state:
        st.text_area("方案详情（可直接复制）：", value=st.session_state.result, height=550)
    else:
        st.info("输入需求并点击生成，哈弗竞标大纲将在此展现。")
