import streamlit as st
import google.generativeai as genai

# --- 必须在第一行 ---
st.set_page_config(page_title="纯视觉生成引擎", layout="wide")

if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 极简状态锁 ---
if 'master_kv' not in st.session_state: st.session_state.master_kv = None
if 'style_locked' not in st.session_state: st.session_state.style_locked = False
if 'style_prompt' not in st.session_state: st.session_state.style_prompt = ""
if 'slide_images' not in st.session_state: st.session_state.slide_images = []

st.title("🦔 Nano Studio：纯视觉生成机")
st.caption("放弃废话，投喂文案，直接干图。")

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.subheader("1. 基础参考")
    ppt_text = st.text_area("在此粘贴你的全套 PPT 文案（作为你出图的备忘参考）：", height=200)
    
    st.markdown("---")
    st.subheader("2. 死磕主视觉 (Master KV)")
    style_input = st.text_input("输入核心视觉风格：", placeholder="例如：哈弗猛龙，荒野与都市交织，高级灰与橙色撞色，留白多")
    
    if st.button("🖼️ 抽一张主调图", type="primary", use_container_width=True):
        if style_input:
            with st.spinner("渲染中..."):
                try:
                    st.session_state.style_prompt = style_input
                    img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                    res = img_model.generate_images(prompt=style_input, number_of_images=1, aspect_ratio="16:9")
                    st.session_state.master_kv = res.images[0]._pil_image
                    st.session_state.style_locked = False
                    st.rerun()
                except Exception as e: st.error(f"出图报错，请检查网络或刷新: {e}")

    if st.session_state.master_kv:
        st.image(st.session_state.master_kv, caption="当前试稿")
        if not st.session_state.style_locked:
            if st.button("✅ 锁定此风格，开始逐页配图", use_container_width=True):
                st.session_state.style_locked = True
                st.rerun()
        else:
            st.success("🔒 风格已锁定")
            if st.button("↩️ 解锁重抽"):
                st.session_state.style_locked = False
                st.rerun()

with col_right:
    st.subheader("3. 逐页配图流水线")
    if not st.session_state.style_locked:
        st.info("👈 请先在左侧抽出满意的主视觉并锁定。")
    else:
        st.write("在此输入下一页的画面要素，系统将强制带入已锁定的基调出图。")
        req = st.text_input("本页需要画什么？", placeholder="例如：一张对比表格的底图，左侧留白，右侧放一台半透明的车")
        
        if st.button("➕ 生成本页配图", type="primary"):
            if req:
                with st.spinner("出图中..."):
                    try:
                        # 强制融合基调
                        combined_prompt = f"A presentation slide background. Elements: {req}. Style MUST strictly match: {st.session_state.style_prompt}. 16:9 ratio, professional PR pitch deck clean layout."
                        img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                        res = img_model.generate_images(prompt=combined_prompt, number_of_images=1, aspect_ratio="16:9")
                        # 倒序插入，让最新生成的图排在最上面
                        st.session_state.slide_images.insert(0, {"req": req, "img": res.images[0]._pil_image})
                        st.rerun()
                    except Exception as e: st.error(f"出图报错: {e}")
        
        if st.session_state.slide_images:
            st.markdown("---")
            for idx, slide in enumerate(st.session_state.slide_images):
                st.write(f"**成图 {len(st.session_state.slide_images) - idx}**: {slide['req']}")
                st.image(slide['img'], use_container_width=True)
                st.markdown("---")
