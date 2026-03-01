import streamlit as st
import google.generativeai as genai

# --- 1. 动力系统 ---
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"].strip())

# --- 2. 状态初始化 (包含视觉子工作流状态) ---
for key in ['step', 'history', 'outline', 'content']:
    if key not in st.session_state:
        st.session_state[key] = "大纲构思" if key == 'step' else ([] if key == 'history' else "")

# 视觉专属状态
if 'master_kv' not in st.session_state: st.session_state.master_kv = None
if 'kv_locked' not in st.session_state: st.session_state.kv_locked = False
if 'slide_deck' not in st.session_state: st.session_state.slide_deck = []

# --- 3. 界面审美 ---
st.set_page_config(page_title="Nano Strategic Studio", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #f7f7f7; }
    section[data-testid="stSidebar"] { background-color: white !important; border-right: 1px solid #eee; width: 420px !important; }
    .canvas-box { background: white; border-radius: 12px; padding: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); border: 1px solid #ddd; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# --- 4. 左侧：宏观流程控制 ---
with st.sidebar:
    st.title("🦔 Nano Studio")
    st.caption("🚀 Paid Tier 3 | 宏观逻辑 + 视觉子工作流")
    
    # 宏观三大步
    st.radio("🎯 宏观工作流", ["大纲构思", "内容填充", "视觉定稿"], key="step")
    
    chat_box = st.container(height=350)
    for m in st.session_state.history:
        chat_box.chat_message(m["role"]).write(m["content"])
    
    # 只有在前两步才使用聊天框控制逻辑
    if st.session_state.step in ["大纲构思", "内容填充"]:
        if user_cmd := st.chat_input("输入策略或内容指令..."):
            st.session_state.history.append({"role": "user", "content": user_cmd})
            with st.spinner("AI 极速处理中..."):
                model = genai.GenerativeModel('gemini-2.5-flash')
                sys_prompt = f"你是公关总监。当前:【{st.session_state.step}】。已定大纲: {st.session_state.outline}。规则: 禁emoji，只输出专业Markdown。如果在写大纲则不输出正文，如果在写正文则严格依照大纲。"
                res = model.generate_content(f"{sys_prompt}\n指令：{user_cmd}")
                
                if st.session_state.step == "大纲构思": st.session_state.outline = res.text
                elif st.session_state.step == "内容填充": st.session_state.content = res.text
                
                st.session_state.history.append({"role": "assistant", "content": f"✅ {st.session_state.step} 已更新。"})
                st.rerun()
    else:
        st.info("🎨 当前处于【视觉定稿】阶段，请在右侧操作面板进行视觉调试。")

# --- 5. 右侧：宏观内容展示 & 视觉子工作流 ---
if st.session_state.step == "大纲构思":
    st.subheader("📍 阶段一：大纲构思 (Anchor)")
    with st.container(border=True):
        st.markdown(st.session_state.outline if st.session_state.outline else "👈 在左侧输入哈弗竞标方向，生成骨架...")

elif st.session_state.step == "内容填充":
    st.subheader("📍 阶段二：深度内容填充 (Execution)")
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.caption("📜 锁定的骨架")
        st.markdown(st.session_state.outline)
    with col2:
        st.caption("📝 详细公关文案")
        st.markdown(st.session_state.content if st.session_state.content else "👈 根据大纲，在左侧发指令生成具体文案...")

elif st.session_state.step == "视觉定稿":
    st.subheader("📍 阶段三：视觉定稿 (KV & Rollout)")
    
    # ==========================================
    # 视觉子工作流 1：死磕 Master KV
    # ==========================================
    if not st.session_state.kv_locked:
        st.markdown("#### 1. 测算并确立主视觉 (Master KV)")
        st.info("在大量生成页面前，先生成一张定调图。不行就一直改，直到满意为止。")
        
        col_ctrl, col_view = st.columns([1, 1.5])
        with col_ctrl:
            v_prompt = st.text_area("输入视觉指令（默认参考大纲）：", value="哈弗猛龙，硬核智电越野，极简高级公关PPT背景图，16:9")
            if st.button("🖼️ 生成/修改 首张测试 KV", type="primary", use_container_width=True):
                with st.spinner("调用 Imagen 3.0 绘图中..."):
                    try:
                        # 确保 SDK 更新后使用最新的标准调用
                        img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                        res = img_model.generate_images(prompt=v_prompt, number_of_images=1, aspect_ratio="16:9")
                        st.session_state.master_kv = res.images[0]._pil_image
                        st.rerun()
                    except Exception as e:
                        st.error(f"绘图异常，请确保 SDK 为最新版: {e}")
            
            if st.session_state.master_kv:
                st.markdown("---")
                if st.button("✅ 满意！锁定此视觉风格，准备陆续出图 ➡️", use_container_width=True):
                    st.session_state.kv_locked = True
                    st.rerun()
                    
        with col_view:
            if st.session_state.master_kv:
                st.markdown('<div class="canvas-box">', unsafe_allow_html=True)
                st.image(st.session_state.master_kv, caption="Master KV 试稿", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="canvas-box" style="text-align:center; color:#999;">等待生成测试图</div>', unsafe_allow_html=True)

    # ==========================================
    # 视觉子工作流 2：延展陆续出图 (Rollout)
    # ==========================================
    else:
        st.markdown("#### 2. 基于主视觉陆续生成页面 (Rollout)")
        col_lock, col_action = st.columns([1, 3])
        
        with col_lock:
            st.caption("🔒 已锁定主视觉调性")
            st.image(st.session_state.master_kv, use_container_width=True)
            if st.button("↩️ 解锁重新定调"):
                st.session_state.kv_locked = False
                st.rerun()
                
        with col_action:
            new_slide = st.text_input("下一页需要什么配图？", placeholder="例如：哈弗猛龙的动力系统透视图 / 竞品对比网格")
            if st.button("➕ 陆续生成下一张图"):
                if new_slide:
                    with st.spinner(f"正在保持风格一致生成：{new_slide}..."):
                        try:
                            img_model = genai.ImageGenerationModel("imagen-3.0-generate-001")
                            res = img_model.generate_images(
                                prompt=f"A presentation slide background for {new_slide}, matching the established high-end Haval PR style, 16:9",
                                number_of_images=1, aspect_ratio="16:9"
                            )
                            st.session_state.slide_deck.append({"topic": new_slide, "img": res.images[0]._pil_image})
                            st.rerun()
                        except Exception as e: st.error(f"出图异常: {e}")
            
            # 展示陆续出图的成果
            st.markdown("---")
            if st.session_state.slide_deck:
                for idx, slide in enumerate(st.session_state.slide_deck):
                    st.write(f"**Slide {idx+1}: {slide['topic']}**")
                    st.image(slide['img'], width=600)
