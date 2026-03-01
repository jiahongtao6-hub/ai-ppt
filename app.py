import streamlit as st
import google.generativeai as genai

# 1. 直接配置 Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

st.set_page_config(page_title="哈弗 PR 实验室", layout="wide")
st.title("🚗 哈弗（Haval）竞标策略中心")
# 引用你账单上的真实数据
st.caption("🚀 权限：Paid Tier 3 | 余额：HK$2,340 | 引擎：Gemini 3.1 Pro")

left, right = st.columns([1, 1.5])

with left:
    prompt = st.text_area("输入哈弗竞标需求（例如：哈弗猛龙传播大纲）：", height=200)
    
    if st.button("🚀 启动 3.1 顶级引擎"):
        if not prompt.strip():
            st.warning("内容不能为空哦！")
        else:
            with st.spinner("正在调用 2026 顶级旗舰模型..."):
                try:
                    # 【核心修正】：使用你诊断列表里支持的最强模型
                    model = genai.GenerativeModel('gemini-3.1-pro-preview') 
                    response = model.generate_content(f"作为哈弗公关专家，请写出 PPT 大纲：{prompt}")
                    st.session_state.result = response.text
                except Exception as e:
                    st.error(f"意外卡顿：{e}。请尝试切换模型名。")

with right:
    if 'result' in st.session_state:
        st.success("✅ 方案生成成功！")
        st.text_area("方案详情：", value=st.session_state.result, height=550)
    else:
        st.info("方案生成后将在此展示。")
