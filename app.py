import streamlit as st
import google.generativeai as genai
import os

# 1. 强制在最顶端设置版本
os.environ["GOOGLE_API_VERSION"] = "v1"

# 2. 读取并清理 Key
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())
else:
    st.error("🔑 没找到 API Key，请检查 Settings -> Secrets")
    st.stop()

# 3. 高审美 UI
st.set_page_config(page_title="哈弗 PR 实验室", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #ff6b00; color: white; border: none; width: 100%; height: 50px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🚗 哈弗（Haval）竞标策略中心")
st.caption("🚀 权限：Paid Tier 3 | 余额：HK$2,340")

left, right = st.columns([1, 1.5])

with left:
    prompt = st.text_area("输入哈弗竞标需求：", placeholder="例如：哈弗猛龙年度公关方案大纲...")
    
    if st.button("🚀 启动 Tier 3 引擎"):
        if not prompt.strip():
            st.warning("请先输入需求哦！")
        else:
            with st.spinner("正在为您尝试所有可用路径..."):
                # 【终极保险逻辑】：依次尝试三个模型名，直到成功
                success = False
                # 尝试顺序：Flash(最稳), Pro(最强), Pro-Latest(备用)
                for model_name in ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.5-pro-latest']:
                    try:
                        model = genai.GenerativeModel(model_name)
                        response = model.generate_content(f"作为哈弗公关专家，请写出 PPT 大纲：{prompt}")
                        st.session_state.result = response.text
                        st.session_state.used_model = model_name
                        success = True
                        break # 只要有一个成功就退出循环
                    except Exception:
                        continue # 失败了就试下一个，不报错
                
                if not success:
                    st.error("所有模型路径均返回 404。请检查 Google Cloud 端的 Generative Language API 是否已启用。")

with right:
    if 'result' in st.session_state:
        st.success(f"✅ 使用模型 {st.session_state.used_model} 生成成功！")
        st.text_area("方案详情：", value=st.session_state.result, height=550)
    else:
        st.info("等待生成哈弗猛龙策略...")
