import streamlit as st
import google.generativeai as genai

# 1. 彻底移除版本锁定，让最新版的 SDK 自己找路
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

st.set_page_config(page_title="哈弗 PR 实验室", layout="wide")
st.title("🚗 哈弗（Haval）竞标策略中心")
st.caption("🚀 权限：Paid Tier 3 | 余额：HK$2,340")

# 2. 诊断：如果 404，点击这里看看到底能用哪些模型
if st.button("🔍 诊断：检查我的可用模型"):
    try:
        model_list = [m.name for m in genai.list_models()]
        st.success(f"诊断成功！你的账号目前支持：{model_list}")
    except Exception as e:
        st.error(f"诊断失败，这说明 API 没在 Google Cloud 后台开启：{e}")

# 3. 核心生成逻辑
prompt = st.text_area("输入哈弗竞标需求：", placeholder="例如：哈弗猛龙年度公关方案大纲...")
if st.button("🚀 生成方案"):
    if not prompt.strip():
        st.warning("请先输入需求内容！")
    else:
        with st.spinner("正在调用最稳定的 Flash 引擎..."):
            try:
                # 优先试最不容易报 404 的模型
                model = genai.GenerativeModel('gemini-1.5-flash')
                response = model.generate_content(f"作为哈弗公关专家，请写出 PPT 大纲：{prompt}")
                st.session_state.result = response.text
                st.success("✅ 生成成功！")
            except Exception as e:
                st.error(f"还是返回了 404。请务必检查 Google Cloud 后台是否开启了 Generative Language API。报错详情：{e}")

if 'result' in st.session_state:
    st.text_area("方案详情：", value=st.session_state.result, height=500)
