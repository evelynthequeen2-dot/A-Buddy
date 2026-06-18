"""A-Buddy — 课程作业智能拆解与进度管理助手（Streamlit 入口）"""

import hashlib
import json
from datetime import datetime

import streamlit as st

from core.analyzer import analyze_assignment_image
from core.db import get_history_item, init_db, list_history, save_history

ALLOWED_TYPES = ["png", "jpg", "jpeg"]


def init_session_state() -> None:
    defaults = {
        "analysis_result": None,
        "analysis_error": None,
        "is_analyzing": False,
        "last_file_hash": None,
        "selected_history_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def file_fingerprint(uploaded_file) -> str:
    data = uploaded_file.getvalue()
    return hashlib.md5(data).hexdigest()


def render_sidebar_history() -> None:
    st.sidebar.title("我的历史拆解")
    history_rows = list_history()

    if not history_rows:
        st.sidebar.caption("还没有历史记录，先上传一张作业截图试试吧。")
        return

    for row in history_rows:
        label = f"{row['file_name']} · {row['created_at']}"
        if st.sidebar.button(label, key=f"history_{row['id']}", width="stretch"):
            st.session_state.selected_history_id = row["id"]
            item = get_history_item(row["id"])
            if item:
                st.session_state.analysis_result = json.loads(item["task_json"])
                st.session_state.analysis_error = None


def persist_analysis_result(file_name: str, result: dict) -> None:
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(file_name=file_name, created_at=created_at, task_data=result)


def render_task_board(result: dict) -> None:
    if result.get("error") == "parse_failed":
        st.error("JSON 解析失败！请看下方 AI 原始输出：")
        st.code(result.get("raw_content", ""))
        return

    deadline = result.get("deadline", "未写明")
    tasks = result.get("tasks", [])

    st.markdown(
        """
        <div class="buddy-result-card">
            <div class="buddy-result-title">🗂️ 任务安排表</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    deadline = st.text_input("📅 截止日期 (可手动修改)", value=str(deadline), key="deadline_input")

    if not tasks:
        st.info("当前没有可展示的任务，请重新解析更清晰的作业要求。")
        return

    progress_placeholder = st.empty()
    task_checkbox_values = []

    for index, task in enumerate(tasks, start=1):
        step_value = task.get("step", index)
        task_name = task.get("task_name", f"任务 {index}")
        details = task.get("details", "")
        task_key = f"task_done_{st.session_state.get('selected_history_id', 'current')}_{index}_{step_value}"
        checked = st.checkbox(f"第 {step_value} 步 · {task_name}", key=task_key)
        task_checkbox_values.append(checked)
        if details:
            st.caption(details)

    completed = sum(1 for checked in task_checkbox_values if checked)
    total = len(task_checkbox_values)
    progress = completed / total if total else 0
    progress_percent = int(progress * 100)
    progress_color = "#ffb7d5" if progress_percent < 34 else "#a8d4f0" if progress_percent < 67 else "#f8a0c4"

    progress_placeholder.markdown(
        f"""
        <div style="background: rgba(255,255,255,0.86); padding: 1rem 1rem 1.1rem; border-radius: 20px; border: 2px solid {progress_color}; box-shadow: 0 8px 24px rgba(248,160,196,0.18); margin-bottom: 1rem;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.55rem; color:#2b2230; font-weight:800;">
                <span>当前进度</span>
                <span>{progress_percent}%</span>
            </div>
            <div style="width:100%; height:16px; background:#f4e9ef; border-radius:999px; overflow:hidden;">
                <div style="width:{progress_percent}%; height:100%; background: linear-gradient(90deg, #ffb7d5 0%, #a8d4f0 100%); border-radius:999px;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
            --text-main: #2b2230;
            --text-body: #352b3d;
            --text-secondary: #4a3d52;
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
            color: var(--text-body);
        }

        .block-container {
            max-width: 720px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .stApp p, .stApp label, .stApp span, .stApp li,
        .stMarkdown, .stMarkdown p, .stMarkdown li,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] li,
        .stCaption, .stText, .stCheckbox label {
            color: var(--text-body) !important;
        }

        .stApp h1, .stApp h2, .stApp h3, .stApp h4,
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h4 {
            color: var(--text-main) !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #FFF5F7 0%, #FFFDFB 100%) !important;
            border-right: 1px solid rgba(255, 183, 213, 0.45);
        }

        [data-testid="stSidebar"] > div {
            background: transparent !important;
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] button {
            color: #4A4A4A !important;
            font-family: 'Nunito', sans-serif !important;
        }

        [data-testid="stSidebar"] .stButton > button,
        [data-testid="stSidebar"] button {
            background: linear-gradient(135deg, #FFE2EC 0%, #FAD7E2 100%) !important;
            color: #4A4A4A !important;
            border: 1px solid rgba(248, 160, 196, 0.6) !important;
            border-radius: 18px !important;
            box-shadow: 0 6px 18px rgba(248, 160, 196, 0.12) !important;
        }

        [data-testid="stSidebar"] .stButton > button:hover,
        [data-testid="stSidebar"] button:hover {
            background: linear-gradient(135deg, #FFD6E8 0%, #FFC7DD 100%) !important;
            color: #2F2F2F !important;
            border-color: rgba(248, 160, 196, 0.8) !important;
        }

        [data-testid="stSidebar"] .stButton > button:focus,
        [data-testid="stSidebar"] button:focus {
            box-shadow: 0 0 0 3px rgba(168, 212, 240, 0.35) !important;
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] .stText {
            color: #4A4A4A !important;
        }

        header[data-testid="stHeader"] {
            background: transparent;
        }

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
            color: var(--text-secondary);
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
            color: #c45e88;
            border: 1.5px solid var(--pink-soft);
        }

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
            color: var(--text-secondary);
            margin-bottom: 0.8rem;
        }

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
            color: var(--text-secondary) !important;
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

        .stButton > button:hover:not(:disabled) {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 28px rgba(248, 160, 196, 0.55) !important;
            background: linear-gradient(135deg, var(--pink-deep) 0%, #f090b8 100%) !important;
        }

        .stButton > button:active:not(:disabled) {
            transform: translateY(0) !important;
        }

        .stButton > button:disabled {
            background: linear-gradient(135deg, #e8d0dc, #dcc8d4) !important;
            color: #6e5e66 !important;
            box-shadow: none !important;
            cursor: not-allowed !important;
            transform: none !important;
        }

        .buddy-tip {
            background: rgba(255, 255, 255, 0.9);
            border-radius: var(--radius-md);
            padding: 1rem 1.2rem;
            margin-top: 1.4rem;
            border-left: 4px solid var(--blue-main);
            font-size: 0.9rem;
            color: var(--text-secondary);
            line-height: 1.65;
        }

        .buddy-tip strong {
            color: var(--text-main);
        }

        .buddy-result-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: var(--radius-lg);
            padding: 1.6rem 1.5rem;
            margin-top: 1.6rem;
            box-shadow: var(--shadow-soft);
            border: 2px solid rgba(255, 255, 255, 0.9);
        }

        .buddy-result-title {
            font-size: 1.15rem;
            font-weight: 800;
            color: var(--text-main);
            margin-bottom: 1rem;
            padding-bottom: 0.6rem;
            border-bottom: 2px dashed var(--pink-soft);
        }

        .buddy-loading {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
            margin: 1.2rem 0;
            background: rgba(255, 255, 255, 0.92);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-soft);
            border: 2px solid var(--blue-soft);
        }

        .buddy-loading-icon {
            font-size: 2.2rem;
            animation: buddy-bounce 1.2s ease-in-out infinite;
        }

        .buddy-loading-dots {
            display: flex;
            gap: 0.5rem;
            margin: 1rem 0 0.6rem;
        }

        .buddy-loading-dots span {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--pink-main), var(--blue-main));
            animation: buddy-dot-pulse 1.4s ease-in-out infinite;
        }

        .buddy-loading-dots span:nth-child(2) {
            animation-delay: 0.2s;
        }

        .buddy-loading-dots span:nth-child(3) {
            animation-delay: 0.4s;
        }

        .buddy-loading-text {
            font-size: 1rem;
            font-weight: 700;
            color: var(--text-main);
            margin: 0;
        }

        .buddy-loading-sub {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 0.4rem;
        }

        @keyframes buddy-bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        @keyframes buddy-dot-pulse {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.5; }
            40% { transform: scale(1); opacity: 1; }
        }

        [data-testid="stImage"] {
            border-radius: var(--radius-md);
            overflow: hidden;
            box-shadow: var(--shadow-soft);
            border: 3px solid white;
        }

        .stAlert {
            border-radius: var(--radius-md) !important;
            font-family: 'Nunito', sans-serif !important;
            color: var(--text-body) !important;
        }

        .buddy-footer {
            text-align: center;
            margin-top: 2.5rem;
            font-size: 0.82rem;
            color: var(--text-secondary);
            opacity: 0.9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_loading_animation() -> None:
    st.markdown(
        """
        <div class="buddy-loading">
            <div class="buddy-loading-icon">🐾</div>
            <div class="buddy-loading-dots">
                <span></span><span></span><span></span>
            </div>
            <p class="buddy-loading-text">学伴正在认真分析作业要求…</p>
            <p class="buddy-loading-sub">请稍候，分析期间请勿重复点击按钮</p>
        </div>
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


def render_analysis_result(result: dict) -> None:
    st.markdown(
        """
        <div class="buddy-result-card">
            <div class="buddy-result-title">📋 拆解分析结果</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f"**截止日期：** {result.get('deadline', '未写明')}")
    tasks = result.get("tasks", [])
    if tasks:
        for task in tasks:
            st.markdown(
                f"- **第 {task.get('step', '')} 步：{task.get('task_name', '')}**\n  - {task.get('details', '')}"
            )
    else:
        st.info("当前解析结果中没有可展示的任务。")


def render_footer() -> None:
    st.markdown(
        """
        <div class="buddy-footer">
            A-Buddy · Assignment Buddy · 李颜美子 · 《人工智能实践》
        </div>
        """,
        unsafe_allow_html=True,
    )


def run_analysis(uploaded_file) -> None:
    st.session_state.is_analyzing = True
    st.session_state.analysis_error = None

    render_loading_animation()

    try:
        image_bytes = uploaded_file.getvalue()
        mime_type = uploaded_file.type or "image/jpeg"
        result = analyze_assignment_image(image_bytes, mime_type)
        st.session_state.analysis_result = result
        st.session_state.last_file_hash = file_fingerprint(uploaded_file)
        persist_analysis_result(uploaded_file.name, result)
    except Exception as exc:
        st.session_state.analysis_result = None
        st.session_state.analysis_error = str(exc)
    finally:
        st.session_state.is_analyzing = False


def main() -> None:
    st.set_page_config(
        page_title="A-Buddy 智能作业拆解",
        page_icon="🐾",
        layout="centered",
        initial_sidebar_state="expanded",
    )

    init_db()
    init_session_state()
    inject_sanrio_theme()
    render_sidebar_history()
    render_header()
    render_upload_section()

    uploaded_file = st.file_uploader(
        "选择作业要求图片",
        type=ALLOWED_TYPES,
        label_visibility="collapsed",
        help="请上传老师发布的作业要求截图或照片",
    )

    if uploaded_file is not None:
        current_hash = file_fingerprint(uploaded_file)
        if st.session_state.last_file_hash and current_hash != st.session_state.last_file_hash:
            st.session_state.analysis_result = None
            st.session_state.analysis_error = None

        st.image(uploaded_file, caption="已选中的作业要求预览", width="stretch")
        st.caption(f"📄 {uploaded_file.name}")

    has_file = uploaded_file is not None
    is_busy = st.session_state.is_analyzing

    if st.button(
        "开始拆解",
        disabled=not has_file or is_busy,
        width="stretch",
        key="analyze_btn",
    ):
        run_analysis(uploaded_file)

    if not has_file and not st.session_state.analysis_result:
        st.markdown(
            """
            <div class="buddy-tip">
                <strong>小提示：</strong>先上传一张作业要求截图，再点击「开始拆解」。
                可以是 PDF 截图、课程计划书照片，或老师发的要求图片哦～
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.analysis_error:
        st.error(f"分析失败：{st.session_state.analysis_error}")

    if st.session_state.analysis_result and not st.session_state.is_analyzing:
        render_task_board(st.session_state.analysis_result)

    render_footer()


if __name__ == "__main__":
    main()
