import streamlit as st
import google.generativeai as genai

# --- 1. 动力引擎 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 2. 铁壁状态锁 (摒弃 Radio，改用整数强制锁定进度) ---
if 'phase' not in st.session_state: st.session_state.phase = 1  # 1:大纲, 2:内容, 3:视觉
if 'doc_data' not in st.session_state: 
    st.session_state.doc_data = {"outline": "", "content": ""}
if 'vis_data' not in st.session_state: 
    st.session_state.vis_data = {"style_prompt": "", "master_kv": None, "is_locked": False, "slides": []}
if 'chat_log' not in st.session_state: st.session_state.chat_log = []

st.set_page_config(page_title="Haval Pitch Studio", layout="wide")

# --- 3. 侧边栏：纯展示进度，不做控制 ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption("🚀 竞标全案流水线")
    st.markdown("---")
    st.write("### 📌 宏观进度")
    st.success("✅ 1. 大纲架构") if st.session_state.phase > 1 else st.info("📍 1. 大纲架构 (当前)")
    st.success("✅ 2. 深度文案") if st.session_state.phase > 2 else (st.info("📍 2. 深度文案 (当前)") if st.session_state.phase == 2 else st.write("⏳ 2. 深度文案"))
    st.success("✅ 3. 视觉出图") if st.session_state.phase > 3 else (st.info("📍 3. 视觉出图 (当前)") if st.session_state.phase == 3 else st.write("⏳ 3. 视觉出图"))
    
    # 强制防错回退按钮
    st.markdown("---")
    if st.session_state.phase > 1:
        if st.button("⚠️ 强制退回上一关", use_container_width=True):
            st.session_state.phase -= 1
            st.rerun()

# ==========================================
# 阶段 1 & 2：大纲与内容 (共用左对话、右画板逻辑)
# ==========================================
if st.session_state.phase in [1, 2]:
    st.header("第一步：大纲" if st.session_state.phase == 1 else "第二步：文案")
    
    col_chat, col_view = st.columns([1, 1.5])
    
    with col_chat:
        chat_box = st.container(height=400)
        for m in st.session_state.chat_log:
            chat_box.chat_message(m["role"]).write(m["content"])
            
        if user_cmd := st.chat_input("输入要求..."):
            st.session_state.chat_log.append({"role": "user", "content": user_cmd})
            with st.spinner("处理中..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                if st.session_state.phase == 1:
                    res = model.generate_content(f"你是公关总监。为哈弗写一份极简PPT大纲。指令：{user_cmd}")
                    st.session_state.doc_data['outline'] = res.text
                else:
                    res = model.generate_content(f"你是公关总监。基于大纲：{st.session_state.doc_data['outline']}，扩写详细页面文案。指令：{user_cmd}")
                    st.session_state.doc_data['content'] = res.text
                st.session_state.chat_log.append({"role": "assistant", "content": "✅ 已更新。"})
                st.rerun()

    with col_view:
        with st.container(border=True):
            st.markdown(st.session_state.doc_data['outline'] if st.session_state.phase == 1 else st.session_state.doc_data['content'])
        
        # 闯关按钮，只有有了内容才能点
        has_data = st.session_state.doc_data['outline'] if st.session_state.phase == 1 else st.session_state.doc_data['content']
        if has_data:
            btn_text = "✅ 确认大纲，进入【深度文案】 ➡️" if st.session_state.phase == 1 else "✅ 确认文案，进入【视觉出图】 ➡️"
            if st.button(btn_text, type="primary"):
                st.session_state.phase += 1
                st.session_state.chat_log = [] # 进入新关卡清空聊天
                st.rerun()

# ==========================================
# 阶段 3：视觉专属流水线 (完全符合你的工作流)
# ==========================================
elif st.session_state.phase == 3:
    st.header("第三步：视觉出图")
    
    # 3.1 试错与定调 (Master KV)
    if not st.session_state.vis_data["is_locked"]:
        st.subheader("1. 先定视觉风格，抽首张 KV")
        
        c_prompt, c_img = st.columns([1, 1.5])
        with c_prompt:
            style_input = st.text_area("输入视觉风格指令：", placeholder="例如：哈弗猛龙，黑橙撞色，赛博朋克风，16:9高级PPT背景")
            if st.button("🖼️ 抽一张看看", type="primary"):
                if style_input:
                    with st.spinner("正在调配风格出图中..."):
                        try:
                            # 保存当前的风格词
                            st.session_state.vis_data["style_prompt"] = style_input
                            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                            res = img_model.generate_images(prompt=style_input, number_of_images=1, aspect_ratio="16:9")
                            st.session_state.vis_data["master_kv"] = res.images[0]._pil_image
                            st.rerun()
                        except Exception as e: st.error(f"出图报错: {e}")
            
            st.info("💡 如果这张不行，就在上面改词继续抽，直到满意为止。")
            
            if st.session_state.vis_data["master_kv"]:
                if st.button("✅ 风格可以，锁定并准备陆续出图", type="primary"):
                    st.session_state.vis_data["is_locked"] = True
                    st.rerun()
                    
        with c_img:
            if st.session_state.vis_data["master_kv"]:
                st.image(st.session_state.vis_data["master_kv"], caption="当前试稿 (Master KV)")
            else:
                st.write("等待抽取第一张图...")

    # 3.2 陆续出图 (Rollout)
    else:
        st.subheader("2. 风格已锁定，陆续出延展图")
        c_lock, c_rollout = st.columns([1, 2])
        
        with c_lock:
            st.write("🔒 **已锁定的视觉基准**")
            st.image(st.session_state.vis_data["master_kv"], use_container_width=True)
            if st.button("↩️ 感觉还是不对，解锁重新定基调"):
                st.session_state.vis_data["is_locked"] = False
                st.rerun()
                
        with c_rollout:
            st.write("📝 **已定稿的文案参考**")
            with st.expander("展开查看之前生成的文案内容"):
                st.write(st.session_state.doc_data['content'])
                
            new_slide_prompt = st.text_input("给下一页出个图（输入具体画面元素）：", placeholder="例如：一张对比表格的背景图，留白要多")
            if st.button("➕ 生成一张新图"):
                if new_slide_prompt:
                    with st.spinner("保持基调陆续出图中..."):
                        try:
                            # 将新的要求和锁定的基调融合出图
                            combined_prompt = f"A presentation background for {new_slide_prompt}, matching this exact style: {st.session_state.vis_data['style_prompt']}, 16:9"
                            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                            res = img_model.generate_images(prompt=combined_prompt, number_of_images=1, aspect_ratio="16:9")
                            
                            st.session_state.vis_data["slides"].append({
                                "req": new_slide_prompt,
                                "img": res.images[0]._pil_image
                            })
                            st.rerun()
                        except Exception as e: st.error(f"出图报错: {e}")
            
            # 展示成果流
            if st.session_state.vis_data["slides"]:
                st.markdown("---")
                for idx, slide in enumerate(st.session_state.vis_data["slides"]):
                    st.write(f"**延展图 {idx+1}**: {slide['req']}")
                    st.image(slide["img"], use_container_width=True)
