import streamlit as st
import google.generativeai as genai
import requests
from io import BytesIO

# --- 1. 动力系统：求稳 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 2. 核心状态：Master KV 优先 ---
if 'workflow_state' not in st.session_state: st.session_state.workflow_state = "1_master_kv" # 1_master_kv 或 2_rollout
if 'style_prompt' not in st.session_state: st.session_state.style_prompt = ""
if 'master_kv_img' not in st.session_state: st.session_state.master_kv_img = None
if 'slides_content' not in st.session_state: st.session_state.slides_content = []

# --- 3. 界面重塑 ---
st.set_page_config(page_title="Haval KV Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    .kv-box { border: 2px solid #ff6b00; border-radius: 12px; padding: 20px; background: #fff; margin-bottom: 20px; }
    .slide-box { border: 1px solid #ddd; border-radius: 8px; padding: 15px; background: #fff; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🦔 Nano Studio：视觉主导工作站")

# ==========================================
# 阶段一：死磕主视觉 (Master KV)
# ==========================================
if st.session_state.workflow_state == "1_master_kv":
    st.markdown("### 📍 第一步：定调核心视觉风格与首张 KV")
    
    col_ctrl, col_view = st.columns([1, 1.5])
    
    with col_ctrl:
        user_style = st.text_area("输入视觉风格与画面构想：", placeholder="例如：哈弗猛龙在夕阳沙漠中疾驰，黑橙撞色，赛博朋克风，适合做PPT封面...")
        
        if st.button("🖼️ 极速生成首张试稿 KV", type="primary", use_container_width=True):
            if user_style:
                with st.spinner("正在调配风格并渲染首图..."):
                    try:
                        # 先用文本模型提炼专业的绘图 Prompt，确保出图质量
                        text_model = genai.GenerativeModel('gemini-2.5-flash')
                        prompt_res = text_model.generate_content(f"将以下想法翻译成极具专业画面感的英文绘图提示词，用于汽车公关竞标PPT的KV背景：{user_style}")
                        st.session_state.style_prompt = prompt_res.text
                        
                        # 【出图修复】：使用最稳妥的 Imagen 3 调用方式
                        # 注意：如果你的 SDK 较老，这里可能会报错。你可以更新 SDK: pip install -U google-generativeai
                        img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                        result = img_model.generate_images(
                            prompt=st.session_state.style_prompt,
                            number_of_images=1,
                            aspect_ratio="16:9"
                        )
                        st.session_state.master_kv_img = result.images[0]._pil_image # 提取 PIL 图像对象
                        st.rerun()
                    except Exception as e:
                        st.error(f"出图失败，请检查 API 权限或 SDK 版本: {e}")
                        st.info("提示：终端运行 `pip install -U google-generativeai` 更新一下。")

        st.markdown("---")
        st.write("💡 **如果第一张不行？**")
        st.write("直接在上方修改你的词，重新点击生成，直到你觉得这张图能拿去给客户提案为止。")

    with col_view:
        if st.session_state.master_kv_img:
            st.markdown('<div class="kv-box">', unsafe_allow_html=True)
            st.image(st.session_state.master_kv_img, caption="首张提案 KV (Master Visual)", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 当有图时，出现进入下一步的按钮
            if st.button("✅ 视觉风格确认，陆续生成后续 PPT 页面 ➡️", use_container_width=True):
                st.session_state.workflow_state = "2_rollout"
                st.rerun()
        else:
            st.info("👈 在左侧输入风格，生成第一张试稿图。")

# ==========================================
# 阶段二：陆续出图与延展 (Rollout)
# ==========================================
elif st.session_state.workflow_state == "2_rollout":
    st.markdown("### 📍 第二步：基于主视觉陆续延展页面")
    
    if st.button("↩️ 返回修改主视觉"):
        st.session_state.workflow_state = "1_master_kv"
        st.rerun()
        
    # 展示已锁定的主视觉
    st.write("已锁定的视觉基调：")
    st.image(st.session_state.master_kv_img, width=300)
    
    st.markdown("---")
    
    col_add, col_list = st.columns([1, 1.5])
    
    with col_add:
        slide_topic = st.text_input("下一页做什么内容？", placeholder="例如：产品核心卖点 / 竞品对比分析")
        if st.button("➕ 生成新一页 (图+文)"):
            if slide_topic:
                with st.spinner(f"正在基于主风格生成【{slide_topic}】..."):
                    try:
                        # 1. 自动写文案
                        text_model = genai.GenerativeModel('gemini-2.5-flash')
                        txt_res = text_model.generate_content(f"为汽车竞标PPT写一页文案。主题：{slide_topic}。要求：专业公关措辞。")
                        
                        # 2. 保持风格一致陆续出图
                        img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                        img_res = img_model.generate_images(
                            prompt=f"A presentation slide background for {slide_topic}, matching this style: {st.session_state.style_prompt}, 16:9, clean layout",
                            number_of_images=1,
                            aspect_ratio="16:9"
                        )
                        
                        # 存入列表
                        st.session_state.slides_content.append({
                            "topic": slide_topic,
                            "text": txt_res.text,
                            "img": img_res.images[0]._pil_image
                        })
                        st.rerun()
                    except Exception as e:
                        st.error(f"延展生成失败: {e}")

    with col_list:
        if not st.session_state.slides_content:
            st.info("👈 输入下一页的主题，开始陆续生成。")
        else:
            for idx, slide in enumerate(st.session_state.slides_content):
                st.markdown(f'<div class="slide-box">', unsafe_allow_html=True)
                st.write(f"**Page {idx+1}: {slide['topic']}**")
                st.image(slide["img"], use_container_width=True)
                st.write(slide["text"])
                st.markdown('</div>', unsafe_allow_html=True)
