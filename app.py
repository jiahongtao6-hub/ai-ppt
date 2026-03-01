import streamlit as st
import google.generativeai as genai

# --- 动力引擎 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 铁壁状态锁：砍掉历史记录，只留核心文档 ---
if 'phase' not in st.session_state: st.session_state.phase = 1 
if 'doc_data' not in st.session_state: st.session_state.doc_data = {"outline": "", "content": ""}
if 'vis_data' not in st.session_state: st.session_state.vis_data = {"style_prompt": "", "master_kv": None, "is_locked": False, "slides": []}

st.set_page_config(page_title="Haval Pitch Studio", layout="wide")

# --- 侧边栏：纯展示进度与防错 ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.write("### 📌 宏观进度")
    st.success("✅ 1. 大纲架构") if st.session_state.phase > 1 else st.info("📍 1. 大纲架构 (当前)")
    st.success("✅ 2. 书面文案") if st.session_state.phase > 2 else (st.info("📍 2. 书面文案 (当前)") if st.session_state.phase == 2 else st.write("⏳ 2. 书面文案"))
    st.success("✅ 3. 视觉定稿") if st.session_state.phase > 3 else (st.info("📍 3. 视觉定稿 (当前)") if st.session_state.phase == 3 else st.write("⏳ 3. 视觉定稿"))
    
    st.markdown("---")
    if st.session_state.phase > 1:
        if st.button("⚠️ 强制退回上一关", use_container_width=True):
            st.session_state.phase -= 1
            st.rerun()
    if st.button("🗑️ 清空全案重来", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 阶段 1：大纲构思 (纯书面输出，无废话)
# ==========================================
if st.session_state.phase == 1:
    st.header("第一步：大纲架构")
    req = st.text_area("输入策略方向（核心打法/痛点/假想敌）：", height=100)
    
    if st.button("📄 生成书面大纲", type="primary"):
        if req:
            with st.spinner("撰写中..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                # 严禁汇报语言的死命令
                sys_prompt = "你是顶级汽车公关策略总监。要求：直接输出结构化的PPT大纲。严禁使用任何客套话、汇报语言（如'好的'、'为您生成'等）。直接输出纯书面报告内容。"
                res = model.generate_content(f"{sys_prompt}\n指令：{req}")
                st.session_state.doc_data['outline'] = res.text
                st.rerun()
                
    if st.session_state.doc_data['outline']:
        with st.container(border=True):
            st.markdown(st.session_state.doc_data['outline'])
        if st.button("✅ 大纲定稿，进入【详细文案】 ➡️", type="primary"):
            st.session_state.phase = 2
            st.rerun()

# ==========================================
# 阶段 2：深度文案 (纯书面输出，无废话)
# ==========================================
elif st.session_state.phase == 2:
    st.header("第二步：书面文案填充")
    with st.expander("查看已定稿大纲"):
        st.write(st.session_state.doc_data['outline'])
        
    req_content = st.text_area("输入文案侧重点或修改意见（留空则直接根据大纲生成全文）：", height=100)
    
    if st.button("📄 生成 PPT 详细书面文案", type="primary"):
        with st.spinner("撰写中..."):
            model = genai.GenerativeModel('gemini-2.5-flash')
            sys_prompt = f"你是顶级汽车公关策略总监。基于以下大纲撰写PPT各页的详细文案内容：\n{st.session_state.doc_data['outline']}\n要求：直接输出PPT排版所需的纯书面内容。严禁使用任何客套话、汇报语言（如'好的'、'为您生成'）。不要解释，直接输出。"
            res = model.generate_content(f"{sys_prompt}\n指令：{req_content}")
            st.session_state.doc_data['content'] = res.text
            st.rerun()
            
    if st.session_state.doc_data['content']:
        with st.container(border=True):
            st.markdown(st.session_state.doc_data['content'])
        if st.button("✅ 文案定稿，进入【视觉出图】 ➡️", type="primary"):
            st.session_state.phase = 3
            st.rerun()

# ==========================================
# 阶段 3：视觉专属流水线 (先定 Master KV，再陆续延展)
# ==========================================
elif st.session_state.phase == 3:
    st.header("第三步：视觉出图")
    
    if not st.session_state.vis_data["is_locked"]:
        st.subheader("1. 盲抽试错：定调 Master KV")
        style_input = st.text_area("输入视觉风格指令：", placeholder="例如：哈弗猛龙，黑橙撞色，科技感，16:9高级PPT背景")
        
        c_btn, c_img = st.columns([1, 2])
        with c_btn:
            if st.button("🖼️ 抽一张主图", type="primary"):
                if style_input:
                    with st.spinner("渲染中..."):
                        try:
                            st.session_state.vis_data["style_prompt"] = style_input
                            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                            res = img_model.generate_images(prompt=style_input, number_of_images=1, aspect_ratio="16:9")
                            st.session_state.vis_data["master_kv"] = res.images[0]._pil_image
                            st.rerun()
                        except Exception as e: st.error(f"出图报错: {e}")
            
            if st.session_state.vis_data["master_kv"]:
                if st.button("✅ 风格锁定，陆续延展出图 ➡️", type="primary"):
                    st.session_state.vis_data["is_locked"] = True
                    st.rerun()
                    
        with c_img:
            if st.session_state.vis_data["master_kv"]:
                st.image(st.session_state.vis_data["master_kv"], caption="当前试稿 (Master KV)")
                
    else:
        st.subheader("2. 陆续延展 (Rollout)")
        c_lock, c_rollout = st.columns([1, 2])
        
        with c_lock:
            st.write("🔒 **主视觉基准**")
            st.image(st.session_state.vis_data["master_kv"])
            if st.button("↩️ 解锁重新定调"):
                st.session_state.vis_data["is_locked"] = False
                st.rerun()
                
        with c_rollout:
            with st.expander("查看文案库"):
                st.write(st.session_state.doc_data['content'])
                
            new_slide = st.text_input("下一张出什么画面？", placeholder="例如：竞品对比矩阵底图，留白多一点")
            if st.button("➕ 生成延展图"):
                if new_slide:
                    with st.spinner("保持基调渲染中..."):
                        try:
                            combined_prompt = f"A presentation background for {new_slide}, matching this exact style: {st.session_state.vis_data['style_prompt']}, 16:9"
                            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                            res = img_model.generate_images(prompt=combined_prompt, number_of_images=1, aspect_ratio="16:9")
                            st.session_state.vis_data["slides"].append({"req": new_slide, "img": res.images[0]._pil_image})
                            st.rerun()
                        except Exception as e: st.error(f"出图报错: {e}")
            
            if st.session_state.vis_data["slides"]:
                st.markdown("---")
                for idx, slide in enumerate(st.session_state.vis_data["slides"]):
                    st.write(f"**延展图 {idx+1}**: {slide['req']}")
                    st.image(slide["img"], use_container_width=True)
