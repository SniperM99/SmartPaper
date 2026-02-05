"""
SmartPaper - Streamlit Web界面版本

运行命令:
    streamlit run gui_streamlit_get_prompt_mode_paper.py

功能:
    提供Web界面让用户输入论文URL，选择提示词模板，并实时显示分析结果
"""

import os
import streamlit as st
from loguru import logger
import yaml
import re
from core.smart_paper_core import SmartPaper
from core.prompt_manager import list_prompts
from typing import List, Dict
import sys
import time
import uuid  # 用于生成用户唯一ID
import traceback  # 用于打印完整的错误栈


def validate_and_format_arxiv_url(url: str) -> str:
    """验证并格式化arXiv URL

    将abs格式转换为pdf格式，并验证URL格式

    Args:
        url: 输入的arXiv URL

    Returns:
        格式化后的URL

    Raises:
        ValueError: 如果URL格式不正确
    """
    logger.debug(f"验证URL格式: {url}")
    # 检查是否是arXiv URL
    arxiv_pattern = r"https?://arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?"
    match = re.match(arxiv_pattern, url)

    if not match:
        logger.warning(f"URL格式不正确: {url}")
        raise ValueError("URL格式不正确，请提供有效的arXiv URL")

    # 提取arXiv ID
    arxiv_id = match.group(2)
    version = match.group(3) or ""

    # 确保使用PDF格式
    formatted_url = f"https://arxiv.org/pdf/{arxiv_id}{version}"

    if match.group(1) == "abs":
        logger.info(f"URL格式已从abs转换为pdf: {url} -> {formatted_url}")
    else:
        logger.debug(f"URL格式已验证: {formatted_url}")

    return formatted_url


def process_paper(input_source, prompt_name: str = "yuanbao", is_file_upload: bool = False):
    """处理论文并以流式方式yield结果"""
    try:
        url = ""
        if not is_file_upload:
            url = input_source
            # 验证并格式化URL
            try:
                url = validate_and_format_arxiv_url(url)
            except ValueError as e:
                logger.error(f"URL验证失败: {str(e)}")
                yield {"type": "final", "success": False, "error": str(e)}
                return
        else:
            # 如果是文件上传
            uploaded_file = input_source
            url = uploaded_file.name  # 使用文件名作为标识

        logger.info(f"使用提示词模板: {prompt_name}")
        logger.info(f"处理目标: {url}")

        # 创建输出目录及输出文件，文件名中加入用户 session_id 避免不同用户间冲突
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        session_id = st.session_state.get("session_id", "default")
        
        # 安全的文件名处理
        safe_name = "".join([c for c in url.split("/")[-1] if c.isalpha() or c.isdigit() or c in ".-_"])
        output_file = os.path.join(
            output_dir, f'analysis_{session_id}_{safe_name}_prompt_{prompt_name}.md'
        )
        logger.info(f"输出文件将保存至: {output_file}\n")

        # 初始化SmartPaper
        logger.debug("初始化SmartPaper")
        reader = SmartPaper(output_format="markdown")

        # 以写入模式打开文件，覆盖旧内容
        logger.debug(f"开始流式处理论文: {url}")
        with open(output_file, "w", encoding="utf-8") as f:
            chunk_count = 0
            total_length = 0
            
            # 获取流生成器
            if is_file_upload:
                # 保存临时文件
                temp_dir = "temp"
                os.makedirs(temp_dir, exist_ok=True)
                file_path = os.path.join(temp_dir, url)
                with open(file_path, "wb") as temp_f:
                    temp_f.write(input_source.getbuffer())
                stream_gen = reader.process_paper_stream(file_path, prompt_name=prompt_name)
            else:
                stream_gen = reader.process_paper_url_stream(url, prompt_name=prompt_name)

            for chunk in stream_gen:
                chunk_count += 1
                total_length += len(chunk)
                f.write(chunk)
                if chunk_count % 10 == 0:  # 每10个块记录一次日志，避免日志过多
                    logger.debug(f"已接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
                yield {"type": "chunk", "content": chunk}

        logger.info(f"分析完成，共接收 {chunk_count} 个响应块，总长度: {total_length} 字符")
        logger.info(f"分析结果已保存到: {output_file}")
        yield {"type": "final", "success": True, "file_path": output_file}

    except Exception as e:
        error_msg = f"处理失败: {str(e)}"
        logger.error(error_msg)
        yield {"type": "chunk", "content": f"❌ **错误**: {error_msg}"}
        yield {"type": "final", "success": False, "error": error_msg}


def reanalyze_paper(url: str, prompt_name: str):
    """重新分析指定URL的论文"""
    logger.info(f"重新分析论文: {url}，使用提示词模板: {prompt_name}")
    # 添加用户请求消息到聊天历史
    st.session_state.messages.append(
        {"role": "user", "content": f"请重新分析论文: {url} 使用提示词模板: {prompt_name}"}
    )

    # 创建进度显示区域
    progress_placeholder = st.empty()

    # 处理论文
    with st.spinner("正在重新分析论文..."):
        full_output = ""
        for result in process_paper(url, prompt_name):
            if result["type"] == "chunk":
                full_output += result["content"]
                # 实时更新进度显示
                progress_placeholder.markdown(full_output)
            elif result["type"] == "final":
                if result["success"]:
                    response = full_output
                    file_path = result["file_path"]
                    file_name = os.path.basename(file_path)
                    logger.info(f"重新分析成功，结果保存至: {file_path}")
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "file_name": file_name,
                        "file_path": file_path,
                        "url": url,  # 保留URL以支持多次重新分析
                    }
                else:
                    logger.error(f"重新分析失败: {result['error']}")
                    response = result["error"]
                    new_message = {
                        "role": "论文分析助手",
                        "content": response,
                        "url": url,  # 即使失败也保留URL
                    }
                st.session_state.messages.append(new_message)
                break

    # 清空进度显示区域
    progress_placeholder.empty()

    # 刷新页面以更新聊天历史
    logger.debug("重新加载页面以更新聊天历史")
    st.rerun()


def main():
    """主函数"""
    logger.info("启动SmartPaperGUI界面")

    # 添加自定义CSS样式
    st.markdown(
        """
    <style>
        /* 整体页面样式 */
        .main {
            background-color: #f8f9fa;
            padding: 20px;
        }

        /* 标题样式 */
        h1 {
            color: #1e3a8a;
            font-weight: 700;
            margin-bottom: 30px;
            text-align: center;
            padding-bottom: 10px;
            border-bottom: 2px solid #3b82f6;
        }

        /* 副标题样式 */
        h3 {
            color: #1e40af;
            font-weight: 600;
            margin-top: 20px;
            margin-bottom: 15px;
            padding-left: 10px;
            border-left: 4px solid #3b82f6;
        }

        /* 聊天消息容器 */
        .stChatMessage {
            border-radius: 10px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* 按钮样式 */
        .stButton>button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        /* 下载按钮样式 */
        .stDownloadButton>button {
            background-color: #4f46e5;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 6px;
        }

        /* 侧边栏样式 */
        .css-1d391kg {
            background-color: #f1f5f9;
            padding: 20px 10px;
        }

        /* 输入框样式 */
        .stTextInput>div>div>input {
            border-radius: 8px;
            border: 1px solid #d1d5db;
            padding: 10px;
        }

        /* URL输入框高亮样式 */
        .url-input {
            border: 2px solid #3b82f6 !important;
            background-color: #eff6ff !important;
            box-shadow: 0 0 10px rgba(59, 130, 246, 0.3) !important;
        }

        /* 选择框样式 */
        .stSelectbox>div>div {
            border-radius: 8px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # 设置页面标题
    st.title("SmartPaper")
    st.markdown(
        """
    <div style="color: gray; font-size: 0.8em;">
        <b>SmartPaper</b>: <a href="https://github.com/sanbuphy/SmartPaper">GitHub</a> -
        一个迷你助手，帮助您快速阅读论文
    </div>
    """,
        unsafe_allow_html=True,
    )

    # 初始化会话状态
    if "messages" not in st.session_state:
        logger.debug("初始化会话状态: messages")
        st.session_state.messages = []
    if "processed_papers" not in st.session_state:
        logger.debug("初始化会话状态: processed_papers")
        st.session_state.processed_papers = {}
    # 为每个用户生成唯一session_id，防止不同用户文件输出冲突
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex

    # 侧边栏配置：仅保留全局配置（提示词模板）
    with st.sidebar:
        st.header("配置选项")
        # 显示可用的提示词模板
        prompt_options = list_prompts()
        logger.debug(f"加载提示词模板，共 {len(prompt_options)} 个")
        
        # 设置默认选中项
        options = list(prompt_options.keys())
        default_index = 0
        target_default = "phd_analysis"
        if target_default in options:
            default_index = options.index(target_default)
            
        selected_prompt = st.selectbox(
            "选择提示词模板",
            options=options,
            index=default_index,
            format_func=lambda x: f"{x}: {prompt_options[x]}",
            help="选择用于分析的提示词模板",
        )
        logger.debug(f"用户选择提示词模板: {selected_prompt}")

    # 创建顶部标签页
    tab_analysis, tab_history = st.tabs(["🚀 当前分析", "📚 历史记录"])

    # === 历史记录标签页 ===
    with tab_history:
        st.header("📚 论文分析历史")
        from core.history_manager import HistoryManager
        import pandas as pd
        
        hm = HistoryManager()
        history = hm.list_history()
        
        if history:
            # --- 删除确认区域 ---
            if "delete_confirm_key" in st.session_state:
                 confirm_key = st.session_state.delete_confirm_key
                 # 查找对应的文件以便显示提示
                 entry_to_del = next((item for item in history if item["cache_key"] == confirm_key), None)
                 fname = entry_to_del['file_name'] if entry_to_del else "该记录"
                 
                 st.warning(f"⚠️ 确定要删除记录: {fname} 吗？(如果是本地文件，同时也会删除结果文件)")
                 col_conf_1, col_conf_2, col_conf_3 = st.columns([0.1, 0.1, 0.8])
                 with col_conf_1:
                     if st.button("✅ 确认", key="btn_confirm_del"):
                         if hm.delete_history_item(confirm_key, delete_file=True):
                                st.success("已删除")
                                del st.session_state.delete_confirm_key
                                time.sleep(0.5)
                                st.rerun()
                         else:
                                st.error("删除失败")
                 with col_conf_2:
                     if st.button("❌ 取消", key="btn_cancel_del"):
                         del st.session_state.delete_confirm_key
                         st.rerun()
                 st.markdown("---")

            # 简单的统计信息
        # === Search & Filter ===
        search_term = st.text_input("🔍 搜索历史记录", placeholder="输入文件名或关键词快速筛选...", label_visibility="collapsed")
        
        # Filter logic
        filtered_history = []
        if search_term:
            search_lower = search_term.lower()
            for item in history:
                name = item.get('file_name', '') or os.path.basename(item.get('original_source', ''))
                if search_lower in name.lower() or search_lower in item.get('prompt_name', '').lower():
                    filtered_history.append(item)
        else:
            filtered_history = history

        if filtered_history:
            # === Pagination ===
            ITEMS_PER_PAGE = 20
            total_items = len(filtered_history)
            total_pages = (total_items + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
            
            if total_pages > 1:
                col_pg1, col_pg2 = st.columns([0.85, 0.15])
                with col_pg2:
                    current_page = st.number_input("页码", min_value=1, max_value=total_pages, value=1, step=1, label_visibility="collapsed")
            else:
                current_page = 1
                
            start_idx = (current_page - 1) * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            displayed_history = filtered_history[start_idx:end_idx]

            # --- HEADER ---
            # Compact header: Time | Template | File Info | Delete
            st.markdown("""
            <style>
            .history-header { font-weight: bold; color: #666; font-size: 0.9em; padding-bottom: 5px; border-bottom: 1px solid #eee; }
            .history-row { padding: 5px 0; border-bottom: 1px solid #f0f0f0; }
            .file-name { font-weight: 600; color: #1e3a8a; font-size: 1.05em; }
            .compact-btn button { padding: 0px 8px !important; height: 28px !important; min-height: 0px !important; font-size: 0.8em !important; }
            </style>
            """, unsafe_allow_html=True)
            
            h_cols = st.columns([0.15, 0.12, 0.63, 0.1])
            h_cols[0].markdown(":grey[分析时间]")
            h_cols[1].markdown(":grey[模板]")
            h_cols[2].markdown(":grey[论文解析内容与操作]")
            h_cols[3].markdown(":grey[删除]")
            # st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True) # Spacer

            # --- LIST ---
            for idx, entry in enumerate(displayed_history):
                # Use a container for better grouping (optional, but keeps css scope tight if needed)
                with st.container():
                     # Main Row Layout
                    cols = st.columns([0.15, 0.12, 0.63, 0.1])
                    
                    # 1. Time
                    ts = pd.to_datetime(entry['timestamp'], unit='s').strftime('%m-%d %H:%M')
                    cols[0].caption(ts)
                    
                    # 2. Template
                    p_name = entry['prompt_name']
                    cols[1].caption(p_name)
                    
                    # 3. File Info & Actions (Combined for compactness)
                    source_name = entry['file_name'] or os.path.basename(entry['original_source'])
                    full_source_path = entry.get('original_source', '')
                    is_local = full_source_path and os.path.exists(full_source_path)
                    
                    with cols[2]:
                        # First line: File Name as a Clickable Button (Triggers Open)
                        # We use help text to show path, and make it look primary or secondary depending on preference
                        help_txt = f"点击打开源文件: {full_source_path}" if is_local else "远程文件无法直接打开"
                        
                        # Use a custom key based on cache_key
                        if st.button(f"📄 {source_name}", key=f"title_btn_{entry['cache_key']}", help=help_txt, disabled=not is_local):
                             try:
                                 import subprocess
                                 subprocess.run(["open", full_source_path], check=True)
                                 st.toast(f"正在打开: {source_name}")
                             except Exception as e:
                                 st.error(f"打开失败: {e}")
                        
                        # Expander for details (Below the button)
                        
                        # Expander for details (Below the buttons, but within the main column flow? Streamlit expander takes full width)
                        # So we put expander BELOW the columns.
                    
                    # 4. Delete
                    with cols[3]:
                        if st.button("🗑️", key=f"dl_{entry['cache_key']}"):
                            st.session_state.delete_confirm_key = entry['cache_key']
                            st.rerun()

                    # Detail Expander (Full Width)
                    with st.expander("👁️ 查看详细解析", expanded=False):
                        file_path = entry['file_path']
                        if os.path.exists(file_path):
                            st.info(f"文件位置: {file_path}")
                            with open(file_path, "r", encoding="utf-8") as f:
                                st.markdown(f.read())
                        else:
                            st.error("结果文件已丢失")
                    
                    # Divider (Minimal)
                    st.markdown("<hr style='margin: 5px 0; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

            # Pagination info footer
            st.caption(f"显示 {start_idx+1}-{min(end_idx, total_items)} / 共 {total_items} 条记录")

        else:
            if search_term:
                 st.info("🔍 未找到匹配的记录")
            else:
                 st.info("暂无历史记录")

    st.markdown("---")

    # === 当前分析标签页 ===
    with tab_analysis:
        st.subheader("选择输入方式")
        # 将原本在侧边栏的输入控件移动到这里
        input_type = st.radio(
            "输入源", 
            ["arXiv URL", "本地PDF文件", "本地目录 (批量)"], 
            horizontal=True,
            key="input_source_radio"
        )

        paper_input = None
        is_file_upload = False
        is_batch_mode = False
        paper_url_display = "" # 用于显示的标识

        if input_type == "arXiv URL":
            # 示例URL列表
            example_urls = [
                "https://arxiv.org/pdf/2305.12002",
                "https://arxiv.org/abs/2310.06825",
                "https://arxiv.org/pdf/2303.08774",
                "https://arxiv.org/abs/2307.09288",
                "https://arxiv.org/pdf/2312.11805",
            ]

            col_ex, col_in = st.columns([1, 2])
            with col_ex:
                # 创建示例URL选择器
                selected_example = st.selectbox(
                    "选择示例论文",
                    options=example_urls,
                    format_func=lambda x: x.split("/")[-1] if "/" in x else x,
                    help="选择一个预设的论文URL作为示例",
                )

            with col_in:
                # 输入论文URL
                paper_url = st.text_input(
                    "论文URL",
                    value=selected_example,
                    help="输入要分析的论文URL (支持arXiv URL，自动转换为PDF格式)",
                    key="paper_url_input",
                )
            
            paper_input = paper_url
            paper_url_display = paper_url
            
            if paper_url != selected_example:
                logger.debug(f"用户输入论文URL: {paper_url}")

        elif input_type == "本地目录 (批量)":
            is_batch_mode = True
            st.info("请输入包含PDF文件的本地目录绝对路径，系统将递归分析所有文件")
            dir_path = st.text_input(
                "目录路径",
                help="输入包含PDF文件的本地目录绝对路径，将递归分析所有文件",
                key="dir_path_input"
            )
            paper_input = dir_path
            paper_url_display = dir_path

        else:
            # 文件上传模式
            uploaded_file = st.file_uploader("上传PDF论文", type=["pdf"], help="上传本地PDF文件进行分析")
            if uploaded_file:
                paper_input = uploaded_file
                is_file_upload = True
                paper_url_display = uploaded_file.name
                logger.debug(f"用户上传文件: {uploaded_file.name}")

        # 操作按钮区域
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if is_batch_mode:
                 process_button = st.button("🚀 开始批量分析", use_container_width=True, type="primary")
            else:
                 process_button = st.button("🚀 开始分析", use_container_width=True, type="primary")
        
        with col2:
            stop_button = st.button("🛑 停止/清空", use_container_width=True)

        if stop_button:
            logger.info("用户清空分析结果")
            st.session_state.messages = []
            st.session_state.processed_papers = {}
            st.rerun()

        st.markdown("---")
        
        # 显示聊天历史（分析结果）
        st.write("### 分析结果")
        chat_container = st.container()

        # 仅在非正在处理状态下渲染此处的历史记录，避免与下方处理逻辑中的渲染冲突导致 duplicate key
        if not process_button:
            with chat_container:
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        # 为已处理的论文显示下载按钮
                        if "file_name" in message:
                            st.download_button(
                                label=f"下载 {message['file_name']}",
                                data=message["content"],
                                file_name=message["file_name"],
                                mime="text/markdown",
                                key=f"download_{message['file_name']}_{i}_{uuid.uuid4().hex[:8]}",
                            )
                        # 添加重新分析功能
                        if "url" in message and not is_batch_mode:
                            with st.expander("重新分析"):
                                prompt_options = list_prompts()
                                selected_prompt_reanalyze = st.selectbox(
                                    "选择提示词模板",
                                    options=list(prompt_options.keys()),
                                    format_func=lambda x: f"{x}: {prompt_options[x]}",
                                    key=f"reanalyze_prompt_{i}",
                                )
                                if st.button("重新分析", key=f"reanalyze_button_{i}"):
                                    logger.info(
                                        f"用户请求重新分析，使用提示词模板: {selected_prompt_reanalyze}"
                                    )
                                    reanalyze_paper(message["url"], selected_prompt_reanalyze)

    # 创建当前分析进展区域
    progress_container = st.container()

    if is_batch_mode and process_button:
        if not paper_input or not os.path.exists(paper_input):
            st.error("请输入有效的目录路径")
            return
            
        # 清空之前的消息
        st.session_state.messages = []
        st.session_state.messages.append({"role": "user", "content": f"开始批量分析目录: {paper_input}"})
        
        from pathlib import Path
        from core.smart_paper_core import SmartPaper # Import SmartPaper for batch processing
        dir_path = Path(paper_input)
        pdf_files = list(dir_path.rglob("*.pdf"))
        total_files = len(pdf_files)
        
        if total_files == 0:
            st.warning("目录中未找到PDF文件")
            return
            
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results_summary = []
        
        try:
             # 初始化Reader
            logger.debug("初始化SmartPaper用于批量处理")
            reader = SmartPaper(output_format="markdown")
            
            # 获取历史记录用于跳过重复
            from core.history_manager import HistoryManager
            hm = HistoryManager()
            history = hm.list_history()
            
            # 构建已处理的文件名集合（从原始路径提取文件名）
            processed_filenames = set()
            for entry in history:
                original_source = entry.get("original_source", "")
                if original_source:
                    # 尝试从路径或URL中提取文件名
                    name = os.path.basename(original_source)
                    if name:
                        processed_filenames.add(name)
            
            for idx, file_path in enumerate(pdf_files):
                status_text.text(f"正在处理 [{idx+1}/{total_files}]: {file_path.name}")
                
                # Check 1: Empty file
                if os.path.getsize(file_path) == 0:
                    logger.warning(f"跳过空文件: {file_path.name}")
                    results_summary.append(f"⚠️ {file_path.name}: 文件为空，已跳过")
                    progress_bar.progress((idx + 1) / total_files)
                    continue

                # Check 2: Skip existing (by filename)
                # 直接检查当前文件名是否在历史记录的文件名集合中
                if file_path.name in processed_filenames:
                    logger.info(f"文件已存在于历史记录中，跳过: {file_path.name}")
                    results_summary.append(f"🔄 {file_path.name}: 已存在 (历史记录)")
                    progress_bar.progress((idx + 1) / total_files)
                    continue

                try:
                    # 使用 st.expander 显示当前正在处理的论文流式输出
                    with st.expander(f"正在分析: {file_path.name}", expanded=True):
                        stream_placeholder = st.empty()
                        full_content = ""
                        
                        # 调用 process_paper_stream
                        # 注意：我们需要确保 process_paper_stream 能够接受本地路径
                        # 查看 smart_paper_core.py, process_paper_stream(file_path, prompt_name) 是存在的
                        
                        # 为了复用保存逻辑，我们需要手动处理流并保存，或者调用 process_paper (非流式)
                        # 但用户想要看流式过程。
                        # SmartPaper.process_paper_stream 只负责 yield 结果，不负责保存到文件(?)
                        # 让我们检查 SmartPaper.process_paper 源码 (Line 80-110 of smart_paper_core.py)
                        # 它是先 process_with_content 获取完整结果，然后再 save_analysis。
                        # process_paper_stream 只是 yield。
                        
                        # 所以我们需要模拟 process_paper 的逻辑但支持流式显示。
                        # 1. 转换PDF
                        # 2. 调用 LLMWrapper.process_stream_with_content
                        # 3. 收集结果
                        # 4. 保存
                        
                        # 简化方案：直接使用 reader.process_paper_stream 获取流，并累积
                        # 然后手动调用 history_manager.save_analysis
                        
                        # 步骤1: 转换 (Reader内部 helper?)
                        # 实际上 reader.process_paper_stream 内部已经做了转换和流式调用。
                        # 让我们看看 process_paper_stream 的实现 (没显示在之前的 view_file 中但它是存在的)
                        # 假设 process_paper_stream 返回 generator yielding chunk string
                        
                        stream_gen = reader.process_paper_stream(str(file_path), prompt_name=selected_prompt)
                        
                        for chunk in stream_gen:
                            full_content += chunk
                            stream_placeholder.markdown(full_content + "▌")
                        
                        stream_placeholder.markdown(full_content)
                        
                        # 步骤2: 保存结果
                        # 需要 metadata (转换结果中的 metadata)
                        # process_paper_stream 可能无法返回 metadata? 
                        # 如果 process_paper_stream 只 yield contents relevant to prompt, we might miss metadata.
                        
                        # 备选方案：由于 SmartPaper API 的限制，如果 process_paper_stream 不返回 metadata，
                        # 我们可能为了流式展示而牺牲 metadata 或者需要修改 core。
                        # 但通常 prompt analysis 不需要复杂的 metadata 除非用于引用。
                        
                        # 让我们尝试构造一个基本的 metadata
                        metadata = {"source": str(file_path), "file_name": file_path.name}
                        
                        # 手动保存
                        # 计算 hash 用于去重/ID
                        import hashlib
                        with open(file_path, "rb") as f:
                            file_hash = hashlib.md5(f.read()).hexdigest()
                            
                        reader.history_manager.save_analysis(
                            source=str(file_path),
                            source_hash=file_hash,
                            prompt_name=selected_prompt,
                            content=full_content,
                            metadata=metadata
                        )
                        
                    results_summary.append(f"✅ {file_path.name}")
                    
                except Exception as e:
                    logger.error(f"处理 {file_path.name} 失败: {e}")
                    results_summary.append(f"❌ {file_path.name}: {str(e)}")
                
                # 更新进度条
                progress_bar.progress((idx + 1) / total_files)
            
            status_text.text("批量分析完成！")
            
            # 显示汇总结果
            summary_text = "### 批量分析报告\n\n" + "\n".join(results_summary)
            st.session_state.messages.append({"role": "论文分析助手", "content": summary_text})
            st.rerun()
            
        except Exception as e:
             st.error(f"批量处理发生错误: {str(e)}")


    # 处理新论文并流式输出
    elif process_button and not is_batch_mode:
        logger.info(f"用户点击开始分析按钮，目标: {paper_url_display}, 提示词模板: {selected_prompt}")

        if not paper_input:
            st.error("请提供有效的论文URL或上传PDF文件")
            return

        # 先验证URL格式 (仅针对URL模式)
        if not is_file_upload:
            try:
                validated_url = validate_and_format_arxiv_url(paper_input)
            except ValueError as exc:
                error_stack = traceback.format_exc()
                logger.error(f"用户输入无效 arXiv URL\n{error_stack}")
                st.error(str(exc))
                st.session_state.messages.append(
                    {
                        "role": "论文分析助手",
                        "content": f"错误: {exc}\n\n详细错误信息:\n{error_stack}",
                        "url": paper_input,
                    }
                )
                st.rerun()
                return
        
        # 检查是否已处理 (使用显示名称作为key)
        # 注意：这里简化处理，对于文件上传可能需要更好的去重机制（如文件hash）
        paper_key = paper_url_display 
        
        if paper_key in st.session_state.processed_papers:
            logger.warning(f"论文已分析过: {paper_key}")
            st.warning('该论文已经分析过，如果不满意，可以点击对应分析结果的"重新分析"按钮。')
        else:
            # 清空之前的消息
            st.session_state.messages = []
            # 添加用户消息到聊天历史
            st.session_state.messages.append(
                {"role": "user", "content": f"请分析论文: {paper_key}"}
            )

            # 在进度容器中创建进度显示区域
            with progress_container:
                st.write("### 当前分析进展\n")
                progress_placeholder = st.empty()

            with st.spinner("正在处理论文..."):
                logger.info(f"开始分析论文: {paper_key}")
                
                # --- Persistence Change Start ---
                # 1. Initialize empty assistant message
                init_msg = {
                    "role": "论文分析助手",
                    "content": "⏳ 正在准备分析...",
                    "url": paper_key
                }
                st.session_state.messages.append(init_msg)
                msg_index = len(st.session_state.messages) - 1
                
                full_output = ""
                for result in process_paper(paper_input, selected_prompt, is_file_upload=is_file_upload):
                    if result["type"] == "chunk":
                        full_output += result["content"]
                        # 2. Real-time update to session state
                        st.session_state.messages[msg_index]["content"] = full_output
                        # Real-time update to placeholder (optional but good for animation)
                        progress_placeholder.markdown(full_output + "▌")
                        
                    elif result["type"] == "final":
                        if result["success"]:
                            logger.info("论文分析成功")
                            response = full_output
                            file_path = result["file_path"]
                            file_name = os.path.basename(file_path)
                            
                            st.session_state.processed_papers[paper_key] = {
                                "content": response,
                                "file_path": file_path,
                                "file_name": file_name,
                            }
                            
                            # 3. Final update to message metadata
                            st.session_state.messages[msg_index]["content"] = response
                            st.session_state.messages[msg_index]["file_name"] = file_name
                            st.session_state.messages[msg_index]["file_path"] = file_path
                            # url is already set
                        else:
                            logger.error(f"论文分析失败: {result['error']}")
                            response = result["error"]
                            # Final update for error
                            st.session_state.messages[msg_index]["content"] = f"❌ 分析出错: {response}"
                        break
                # --- Persistence Change End ---

            # 分析完成后清空进度显示
            progress_placeholder.empty()

            # 更新聊天历史显示
            with chat_container:
                for i, message in enumerate(st.session_state.messages):
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        if "file_name" in message:
                            st.download_button(
                                label=f"下载 {message['file_name']}",
                                data=message["content"],
                                file_name=message["file_name"],
                                mime="text/markdown",
                                key=f"download_{message['file_name']}_{i}_{uuid.uuid4().hex[:8]}",
                            )
                        if "url" in message:
                            with st.expander("重新分析"):
                                prompt_options = list_prompts()
                                selected_prompt_reanalyze = st.selectbox(
                                    "选择提示词模板",
                                    options=list(prompt_options.keys()),
                                    format_func=lambda x: f"{x}: {prompt_options[x]}",
                                    key=f"reanalyze_prompt_{i}",
                                )
                                if st.button("重新分析", key=f"reanalyze_button_{i}"):
                                    logger.info(
                                        f"用户请求重新分析，使用提示词模板: {selected_prompt_reanalyze}"
                                    )
                                    reanalyze_paper(message["url"], selected_prompt_reanalyze)


if __name__ == "__main__":
    # 配置日志记录
    logger.remove()  # 移除默认处理器
    # 只输出到控制台，不记录到文件
    logger.add(
        sys.stdout,
        level="INFO",
        format="{time:HH:mm:ss} | <level>{level: <8}</level> | {message}",
        colorize=True,
    )

    logger.info("=== SmartPaperGUI启动 ===")

    # 创建必要的目录
    os.makedirs("outputs", exist_ok=True)

    # 配置Streamlit页面
    st.set_page_config(
        page_title="SmartPaper", page_icon="📄", layout="wide", initial_sidebar_state="expanded"
    )

    # 运行主函数
    main()
