"""A-Buddy — 课程作业智能拆解与进度管理助手（Streamlit 入口）"""

import streamlit as st

ALLOWED_TYPES = ["png", "jpg", "jpeg"]


def inject_sanrio_theme() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

        :root {
            --pink-soft: #ffd6e8;
            --pink-main: #ffb7d5;
            --pink-deep: #f8a0c4;
            --blue-soft: #d8effa;
            --blue-main: #a8d4f0;
            --blue-deep: #7eb8e3;
            --cream: #fff9fc;
            --white: #ffffff;
            --text-main: #5a4a5e;
            --text-light: #8a7a8e;
            --shadow-soft: 0 8px 32px rgba(255, 183, 213, 0.25);
            --radius-lg: 28px;
            --radius-md: 20px;
            --radius-pill: 999px;
        }

        .stApp {
            background: linear-gradient(
                165deg,
                var(--cream) 0%,
                var(--blue-soft) 45%,
                var(--pink-soft) 100%
            );
            font-family: 'Nunito', sans-serif;
        }

        .block-container {
            max-width: 720px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        /* 隐藏默认页眉留白感 */
        header[data-testid="stHeader"] {
            background: transparent;
        }

        /* 自定义页头卡片 */
        .buddy-header {
            text-align: center;
            padding: 2.2rem 1.8rem 1.6rem;
            margin-bottom: 1.8rem;
            background: linear-gradient(
                135deg,
                rgba(255, 255, 255, 0.92) 0%,
                rgba(216, 239, 250, 0.75) 50%,
                rgba(255, 214, 232, 0.75) 100%
            );
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-soft);
            border: 2px solid rgba(255, 255, 255, 0.8);
            position: relative;
            overflow: hidden;
        }

        .buddy-header::before,
        .buddy-header::after {
            content: '';
            position: absolute;
            border-radius: 50%;
            opacity: 0.45;
        }

        .buddy-header::before {
            width: 120px;
            height: 120px;
            background: radial-gradient(circle, var(--pink-main) 0%, transparent 70%);
            top: -40px;
            right: -20px;
        }

        .buddy-header::after {
            width: 90px;
            height: 90px;
            background: radial-gradient(circle, var(--blue-main) 0%, transparent 70%);
            bottom: -30px;
            left: -15px;
        }

        .buddy-logo {
            font-size: 2.6rem;
            margin-bottom: 0.3rem;
            filter: drop-shadow(0 2px 4px rgba(248, 160, 196, 0.3));
        }

        .buddy-title {
            font-size: 1.85rem;
            font-weight: 800;
            color: var(--text-main);
            margin: 0 0 0.5rem 0;
            letter-spacing: 0.02em;
        }

        .buddy-subtitle {
            font-size: 1rem;
            font-weight: 600;
            color: var(--text-light);
            margin: 0;
            line-height: 1.6;
        }

        .buddy-tagline {
            display: inline-block;
            margin-top: 1rem;
            padding: 0.45rem 1.2rem;
            background: rgba(255, 255, 255, 0.85);
            border-radius: var(--radius-pill);
            font-size: 0.88rem;
            font-weight: 700;
            color: var(--pink-deep);
            border: 1.5px solid var(--pink-soft);
        }

        /* 上传区域卡片 */
        .upload-card {
            background: rgba(255, 255, 255, 0.88);
            border-radius: var(--radius-lg);
            padding: 1.6rem 1.4rem 0.4rem;
            margin-bottom: 1.2rem;
            box-shadow: var(--shadow-soft);
            border: 2px dashed var(--blue-main);
        }

        .upload-card-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 0.3rem;
        }

        .upload-card-hint {
            font-size: 0.85rem;
            color: var(--text-light);
            margin-bottom: 0.8rem;
        }

        /* 文件上传组件 */
        [data-testid="stFileUploader"] {
            background: var(--blue-soft);
            border-radius: var(--radius-md);
            padding: 0.6rem;
            border: none;
        }

        [data-testid="stFileUploader"] section {
            border: 2px dashed var(--blue-deep) !important;
            border-radius: var(--radius-md) !important;
            background: rgba(255, 255, 255, 0.7) !important;
            padding: 1.2rem !important;
        }

        [data-testid="stFileUploader"] section:hover {
            border-color: var(--pink-deep) !important;
            background: rgba(255, 249, 252, 0.95) !important;
        }

        [data-testid="stFileUploader"] small {
            color: var(--text-light) !important;
            font-family: 'Nunito', sans-serif !important;
        }

        [data-testid="stFileUploader"] button {
            background: linear-gradient(135deg, var(--blue-main), var(--blue-deep)) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-pill) !important;
            font-family: 'Nunito', sans-serif !important;
            font-weight: 700 !important;
            padding: 0.5rem 1.4rem !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        [data-testid="stFileUploader"] button:hover {
            transform: translateY(-1px) !important;
            box-shadow: 0 4px 16px rgba(126, 184, 227, 0.45) !important;
        }

        /* 主操作按钮 */
        .stButton > button {
            width: 100%;
            background: linear-gradient(135deg, var(--pink-main) 0%, var(--pink-deep) 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: var(--radius-pill) !important;
            padding: 0.85rem 2rem !important;
            font-family: 'Nunito', sans-serif !important;
            font-size: 1.1rem !important;
            font-weight: 800 !important;
            letter-spacing: 0.04em !important;
            box-shadow: 0 6px 24px rgba(248, 160, 196, 0.45) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }

        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 28px rgba(248, 160, 196, 0.55) !important;
            background: linear-gradient(135deg, var(--pink-deep) 0%, #f090b8 100%) !important;
        }

        .stButton > button:active {
            transform: translateY(0) !important;
        }

        .stButton > button:disabled {
            background: linear-gradient(135deg, #e8d0dc, #dcc8d4) !important;
            color: #a09098 !important;
            box-shadow: none !important;
            cursor: not-allowed !important;
            transform: none !important;
        }

        /* 提示信息框 */
        .buddy-tip {
            background: rgba(255, 255, 255, 0.82);
            border-radius: var(--radius-md);
            padding: 1rem 1.2rem;
            margin-top: 1.4rem;
            border-left: 4px solid var(--blue-main);
            font-size: 0.9rem;
            color: var(--text-light);
            line-height: 1.65;
        }

        .buddy-tip strong {
            color: var(--text-main);
        }

        /* 预览区 */
        [data-testid="stImage"] {
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-soft);
            border: 3px solid white;
        }

        /* Streamlit 自带 alert 圆角化 */
        .stAlert {
            border-radius: var(--radius-md) !important;
            font-family: 'Nunito', sans-serif !important;
        }

        /* 页脚 */
        .buddy-footer {
            text-align: center;
            margin-top: 2.5rem;
            font-size: 0.82rem;
            color: var(--text-light);
            opacity: 0.85;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="buddy-header">
            <div class="buddy-logo">🐾</div>
            <h1 class="buddy-title">A-Buddy 智能作业拆解</h1>
            <p class="buddy-subtitle">
                上传作业要求，让学伴帮你理清每一步<br>
                告别期末焦虑，从「知道今天做什么」开始
            </p>
            <span class="buddy-tagline">✨ 陪伴你度过每一个 DDL</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_upload_section() -> None:
    st.markdown(
        """
        <div class="upload-card">
            <div class="upload-card-title">📎 上传作业要求</div>
            <div class="upload-card-hint">支持 PNG / JPG / JPEG · 拍照或截图都可以</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        """
        <div class="buddy-footer">
            A-Buddy · Assignment Buddy · 李颜美子 · 《人工智能实践》
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="A-Buddy 智能作业拆解",
        page_icon="🐾",
        layout="centered",
        initial_sidebar_state="collapsed",
    )

    inject_sanrio_theme()
    render_header()
    render_upload_section()

    uploaded_file = st.file_uploader(
        "选择作业要求图片",
        type=ALLOWED_TYPES,
        label_visibility="collapsed",
        help="请上传老师发布的作业要求截图或照片",
    )

    if uploaded_file is not None:
        st.session_state["uploaded_file"] = uploaded_file
        st.image(uploaded_file, caption="已选中的作业要求预览", use_container_width=True)
        st.caption(f"📄 {uploaded_file.name}")

    has_file = uploaded_file is not None

    if st.button("开始拆解", disabled=not has_file, use_container_width=True):
        st.session_state["analyze_requested"] = True
        with st.spinner("🌸 学伴正在认真阅读你的作业要求…"):
            # 占位：后续接入 Gemini Vision 解析引擎
            st.success("已收到作业要求！解析引擎将在下一步接入。")

    if not has_file:
        st.markdown(
            """
            <div class="buddy-tip">
                <strong>小提示：</strong>先上传一张作业要求截图，再点击「开始拆解」。
                可以是 PDF 截图、课程计划书照片，或老师发的要求图片哦～
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_footer()


if __name__ == "__main__":
    main()
