import streamlit as st
import google.generativeai as genai
import os

# 1. 强制锁定 v1 正式版通道
os.environ["GOOGLE_API_VERSION"] = "v1"

# 2. 读取 Secrets
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# 3. 高审美 UI (仿 Nano Studio)
st.set_page_config(page_title="哈弗 PR 实验室", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .card { background: rgba(255,255,255,0.05); border-radius: 15px; padding: 20px; border: 1px solid rgba(255,255,255,0.1); }
    .stButton>button { background-color: #ff6b00; color: white; border: none; height: 45px; width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 哈弗（Haval）竞标策略中心")
st.caption("🚀 当前层级：Paid Tier 3 (无限制生成)")

left, right = st.columns([1, 1.5])

with left:
    st.markdown("### 1. 风格预设")
    st.markdown('<div class="card">🔥 硬核越野 | ⚡ 智电科技</div>', unsafe_allow_html=True)
    
    # 增加一个默认值，防止空输入报错
    prompt = st.text_area("输入你的竞标核心点：", placeholder="例如：哈弗猛龙 2026 传播方案...")
    
    if st.button("🚀 生成方案"):
        if not prompt.strip():
            st.warning("⚠️ 哥，先在上面框里写点关于哈弗的需求呀！")
        else:
            with st.spinner("正在调用 Tier 3 顶级逻辑..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    response = model.generate_content(f"作为哈弗公关专家，请写出 PPT 大纲：{prompt}")
                    st.session_state.result = response.text
                except Exception as e:
                    st.error(f"发生意外：{e}")

with right:
    st.markdown("### 🖼️ 实时预览")
    if 'result' in st.session_state:
        st.text_area("大纲详情：", value=st.session_state.result, height=500)
    else:
        st.info("方案生成后将显示在这里。")
