"""SmartPaper Streamlit 工作台

统一串联论文导入、论文库管理、跨论文分析、研究映射与 Zotero 接入入口。
"""
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
from loguru import logger

try:
    from application.multi_paper_service import MultiPaperService
    from application.paper_analysis_service import PaperAnalysisService
    from application.workbench_service import WorkbenchService
    from interfaces.web.workbench_state import (
        build_overview_metrics,
        build_workflow_steps,
        compare_panel_state,
        create_zotero_placeholder_batch,
        ensure_session_defaults,
        filter_library_entries,
        research_map_scope,
    )
    from src.core.config_loader import load_config
    from src.core.prompt_manager import get_available_options
except ImportError as e:
    st.error(f"严重导入错误: {e}")
    st.stop()

WORKSPACES = {
    "overview": "🧭 工作台总览",
    "intake": "📥 导入与解析",
    "library": "📚 论文库",
    "analysis": "🧠 分析工作流",
    "zotero": "🗂️ Zotero 集成",
}


def validate_and_format_arxiv_url(url: str) -> str:
    arxiv_pattern = r"https?://arxiv\.org/(abs|pdf)/(\d+\.\d+)(v\d+)?"
    match = re.match(arxiv_pattern, url.strip())
    if not match:
        raise ValueError("URL 格式不正确，请提供有效的 arXiv URL")
    arxiv_id = match.group(2)
    version = match.group(3) or ""
    return f"https://arxiv.org/pdf/{arxiv_id}{version}"


def init_session_state() -> None:
    defaults = ensure_session_defaults({"session_id": uuid.uuid4().hex})
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def goto_workspace(workspace_key: str) -> None:
    st.session_state.workspace = workspace_key
    st.rerun()


def get_entry_by_key(cache_key: Optional[str], entries: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not cache_key:
        return None
    for entry in entries:
        if entry["cache_key"] == cache_key:
            return entry
    return None


def process_paper(
    input_source,
    role: str,
    task: str,
    domain: str,
    use_chain: bool = False,
    is_file_upload: bool = False,
    is_local_path: bool = False,
):
    try:
        if is_local_path:
            display_name = os.path.basename(str(input_source))
        elif is_file_upload:
            display_name = input_source.name
        else:
            display_name = validate_and_format_arxiv_url(str(input_source))

        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        safe_name = "".join(c for c in display_name.split("/")[-1] if c.isalnum() or c in ".-_")
        output_file = os.path.join(output_dir, f"analysis_{st.session_state.session_id}_{safe_name}_{task}.md")
        service = PaperAnalysisService(load_config())

        with open(output_file, "w", encoding="utf-8") as f:
            if is_file_upload:
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                file_path = temp_dir / display_name
                with open(file_path, "wb") as temp_f:
                    temp_f.write(input_source.getbuffer())
                stream_gen = service.analyze_stream(str(file_path), role=role, task=task, domain=domain)
            elif is_local_path:
                stream_gen = service.analyze_stream(str(input_source), role=role, task=task, domain=domain)
            else:
                stream_gen = service.analyze_url_stream(display_name, role=role, task=task, domain=domain)

            for chunk in stream_gen:
                f.write(chunk)
                yield {"type": "chunk", "content": chunk}

        yield {"type": "final", "success": True, "file_path": output_file}
    except Exception as exc:
        logger.exception("处理论文失败")
        yield {"type": "chunk", "content": f"\n\n❌ **错误**: {exc}"}
        yield {"type": "final", "success": False, "error": str(exc)}


def render_profile_editor(workbench_service: WorkbenchService) -> None:
    profile = workbench_service.get_profile()
    with st.expander("👤 我的科研画像", expanded=False):
        ctx = profile.get("user_context", {})
        new_role = st.text_input("身份/角色", value=ctx.get("role", "PhD Student"))
        new_area = st.text_input("研究领域", value=ctx.get("research_area", "Industrial AI"))
        new_project = st.text_area("当前课题", value=ctx.get("current_project", ""))
        interests = profile.get("interests", [])
        new_interests = st.text_area("关注关键词（分号分隔）", value="; ".join(interests))
        focus = profile.get("analysis_focus", [])
        new_focus = st.text_area("分析侧重（分号分隔）", value="; ".join(focus))
        if st.button("保存科研画像", use_container_width=True):
            profile["user_context"] = {
                "role": new_role,
                "research_area": new_area,
                "current_project": new_project,
            }
            profile["interests"] = [i.strip() for i in new_interests.split(";") if i.strip()]
            profile["analysis_focus"] = [i.strip() for i in new_focus.split(";") if i.strip()]
            workbench_service.update_profile(profile)
            st.success("科研画像已更新")
            st.rerun()

def render_sidebar(options: Dict[str, Any], entries: List[Dict[str, Any]], workbench_service: WorkbenchService) -> Dict[str, str]:
    with st.sidebar:
        st.header("🧭 工作台导航")
        # 使用 selectbox 替代 radio 避免双击问题
        selected_workspace = st.selectbox(
            "当前页面",
            options=list(WORKSPACES.keys()),
            format_func=lambda key: WORKSPACES[key],
            index=list(WORKSPACES.keys()).index(st.session_state.workspace),
            key="workspace_selector"
        )
        if selected_workspace != st.session_state.workspace:
            st.session_state.workspace = selected_workspace
            st.rerun()

        active_entry = get_entry_by_key(st.session_state.active_paper_key, entries)
        st.caption(
            f"论文库 {len(entries)} 篇｜当前主论文 {active_entry['title'] if active_entry else '未选择'}｜对比集 {len(st.session_state.compare_keys)} 篇"
        )
        st.progress(min(len(st.session_state.compare_keys), 5) / 5 if entries else 0.0, text="多论文对比准备度")

        st.markdown("---")
        st.subheader("🎭 分析配置")
        sel_role = st.selectbox(
            "角色",
            options=list(options["roles"].keys()),
            format_func=lambda x: f"{x}: {options['roles'][x]}",
            index=0,
        )
        sel_domain = st.selectbox(
            "领域背景",
            options=list(options["domains"].keys()),
            format_func=lambda x: f"{x}: {options['domains'][x]}",
            index=0,
        )
        task_options = {**options["tasks"], **options["prompts"]}
        default_task = "phd_analysis" if "phd_analysis" in task_options else list(task_options.keys())[0]
        sel_task = st.selectbox(
            "任务 / 预设",
            options=list(task_options.keys()),
            format_func=lambda x: f"{x}: {task_options[x]}",
            index=list(task_options.keys()).index(default_task),
        )
        use_chain = st.checkbox("开启多轮深度分析链", value=False)
        st.caption("📝 多轮分析链会进行更深度的对话式分析，逐步挖掘论文的核心内容和方法论细节")

        st.markdown("---")
        render_profile_editor(workbench_service)
    return {"role": sel_role, "domain": sel_domain, "task": sel_task, "use_chain": use_chain}


def render_overview(entries: List[Dict[str, Any]]) -> None:
    st.header("🧭 SmartPaper 统一工作台")
    st.caption("推荐流程：导入解析 → 论文入库 → 单篇查看/追溯 → 多篇对比 → 研究映射 → Zotero 导入补全")

    metrics = build_overview_metrics(entries, st.session_state.active_paper_key, st.session_state.compare_keys, st.session_state.zotero_batches)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("论文总数", metrics["paper_count"])
    col2.metric("当前主论文", metrics["active_paper_count"])
    col3.metric("对比集合", metrics["compare_count"])
    col4.metric("Zotero 批次", metrics["zotero_batch_count"])

    quick1, quick2, quick3, quick4 = st.columns(4)
    if quick1.button("去导入解析", use_container_width=True):
        goto_workspace("intake")
    if quick2.button("查看论文库", use_container_width=True):
        goto_workspace("library")
    if quick3.button("进入分析流", use_container_width=True):
        goto_workspace("analysis")
    if quick4.button("打开 Zotero", use_container_width=True):
        goto_workspace("zotero")

    st.markdown("---")
    left, right = st.columns([0.6, 0.4])
    with left:
        st.subheader("近期论文")
        if not entries:
            st.info("当前论文库为空，请先前往“导入与解析”。")
        else:
            for entry in entries[:5]:
                with st.container(border=True):
                    st.markdown(f"**{entry['title']}**")
                    st.caption(f"{entry['year']} · {entry['venue']} · {entry['prompt_name']}")
                    st.write(entry['summary'])
                    action_col1, action_col2 = st.columns(2)
                    if action_col1.button("设为主论文", key=f"overview_active_{entry['cache_key']}", use_container_width=True):
                        st.session_state.active_paper_key = entry["cache_key"]
                        goto_workspace("analysis")
                    if action_col2.button("加入对比", key=f"overview_compare_{entry['cache_key']}", use_container_width=True):
                        if entry["cache_key"] not in st.session_state.compare_keys:
                            st.session_state.compare_keys.append(entry["cache_key"])
                        st.success("已加入对比集合")
    with right:
        st.subheader("当前工作流状态")
        for item in build_workflow_steps(entries, st.session_state.active_paper_key, st.session_state.compare_keys):
            st.write(f"- **{item['step']}**：{item['status']}")
        if st.session_state.last_analysis_output:
            st.markdown("---")
            st.subheader("最近一次解析结果")
            st.code(st.session_state.last_analysis_output, language="markdown")


def render_import_workspace(config: Dict[str, str]) -> None:
    st.header("📥 导入与解析")
    st.caption("统一支持 arXiv、本地 PDF、目录批量导入，并为 Zotero 导入预留同样的后续流转入口。")

    tab1, tab2, tab3 = st.tabs(["单篇解析", "批量目录", "Zotero 导入入口"])

    with tab1:
        input_type = st.radio("输入源", ["arXiv URL", "本地 PDF"], horizontal=True)
        paper_input = None
        is_file_upload = False
        if input_type == "arXiv URL":
            paper_input = st.text_input("arXiv URL", value="https://arxiv.org/abs/2305.12002")
        else:
            upload = st.file_uploader("上传 PDF 文件", type=["pdf"], key="single_pdf_upload")
            if upload:
                paper_input = upload
                is_file_upload = True

        if st.button("开始解析并入库", type="primary", use_container_width=True):
            if not paper_input:
                st.warning("请先提供 URL 或上传 PDF。")
            else:
                placeholder = st.empty()
                full_output = ""
                with st.spinner("正在解析论文..."):
                    for result in process_paper(
                        paper_input,
                        role=config["role"],
                        task=config["task"],
                        domain=config["domain"],
                        use_chain=config["use_chain"],
                        is_file_upload=is_file_upload,
                    ):
                        if result["type"] == "chunk":
                            full_output += result["content"]
                            placeholder.markdown(full_output + "▌")
                        elif result["type"] == "final":
                            if result["success"]:
                                st.session_state.last_analysis_output = full_output
                                st.success("解析完成，结果已写入论文库。")
                            else:
                                st.error(f"解析失败：{result.get('error', '未知错误')}")
                st.rerun()

    with tab2:
        st.info("💡 请输入本地文件夹的完整路径，例如：/Users/yourname/Documents/Papers 或 C:\\Users\\yourname\\Documents\\Papers")

        # 提供路径输入和常用路径快速选择
        col1, col2 = st.columns([3, 1])

        with col1:
            dir_path = st.text_input(
                "PDF 目录路径",
                placeholder="例如：/Users/yourname/Documents/Papers",
                value=st.session_state.get("last_dir_path", ""),
                key="batch_dir_path"
            )

        with col2:
            if st.button("预览目录", use_container_width=True, type="secondary"):
                if dir_path and Path(dir_path).exists():
                    pdf_files = list(Path(dir_path).rglob("*.pdf"))
                    st.success(f"找到 {len(pdf_files)} 个 PDF 文件")
                    st.session_state.preview_pdf_count = len(pdf_files)
                else:
                    st.warning("目录不存在或为空")

        # 显示预览信息
        if "preview_pdf_count" in st.session_state:
            st.caption(f"📁 当前目录包含 {st.session_state.preview_pdf_count} 个 PDF 文件")

        if st.button("批量解析目录", use_container_width=True, type="primary"):
            if not dir_path:
                st.warning("请先填写目录路径。")
            else:
                # 保存最后使用的路径
                st.session_state.last_dir_path = dir_path
                pdf_files = [str(f) for f in Path(dir_path).rglob("*.pdf")] if Path(dir_path).exists() else []
                if not pdf_files:
                    st.warning("目录中未找到 PDF 文件。")
                else:
                    service = PaperAnalysisService(load_config())
                    progress = st.progress(0.0)
                    status = st.empty()
                    for idx, file_path in enumerate(pdf_files, start=1):
                        status.info(f"正在处理：{Path(file_path).name}")
                        service.analyze_file(
                            file_path,
                            role=config["role"],
                            task=config["task"],
                            domain=config["domain"],
                            use_chain=config["use_chain"],
                        )
                        progress.progress(idx / len(pdf_files), text=f"{idx}/{len(pdf_files)}")
                    st.success(f"批量解析完成，共处理 {len(pdf_files)} 篇。")
                    st.rerun()

    with tab3:
        st.info("Zotero 后端同步接口尚未在当前仓库落地。此处先提供统一入口、映射配置和批次记录，便于后续直接接入真实 API。")
        library_name = st.text_input("Zotero Library / Collection", placeholder="My Library / AI-Papers")
        export_files = st.file_uploader(
            "上传 Zotero 导出文件或附件清单",
            type=["json", "csv", "ris", "bib", "txt", "zip"],
            accept_multiple_files=True,
            key="zotero_seed_files",
        )
        mapping_mode = st.selectbox("导入映射策略", ["条目 + 附件", "仅条目", "条目 + 标签 + Collections"])
        if st.button("记录 Zotero 导入批次", use_container_width=True):
            batch = create_zotero_placeholder_batch(
                library_name=library_name,
                mapping_mode=mapping_mode,
                files=[f.name for f in (export_files or [])],
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            )
            st.session_state.zotero_batches.insert(0, batch)
            st.success("已记录导入批次，后续接入 Zotero 服务后可复用该配置。")


def render_library_workspace(entries: List[Dict[str, Any]]) -> None:
    st.header("📚 论文库")
    st.caption("统一提供筛选、卡片详情、追溯信息、单篇主论文选择和多篇对比选集。")

    if not entries:
        st.info("论文库为空，请先完成导入解析。")
        return

    query_col, year_col, task_col = st.columns([0.5, 0.2, 0.3])
    query = query_col.text_input("搜索标题 / 来源 / 关键词", value=st.session_state.library_query)
    st.session_state.library_query = query
    years = [str(item["year"]) for item in entries if str(item["year"]).strip()]
    selected_year = year_col.selectbox("年份", ["全部"] + sorted(set(years), reverse=True))
    task_options = ["全部"] + sorted({item["prompt_name"] for item in entries})
    selected_task = task_col.selectbox("任务", task_options)

    filtered = filter_library_entries(entries, query=query, selected_year=selected_year, selected_task=selected_task)

    st.write(f"筛选后共 {len(filtered)} 篇")
    for entry in filtered:
        selected_for_compare = entry["cache_key"] in st.session_state.compare_keys
        with st.container(border=True):
            title_col, meta_col = st.columns([0.7, 0.3])
            with title_col:
                st.markdown(f"### {entry['title']}")
                st.caption(f"{entry['year']} · {entry['venue']} · {entry['prompt_name']}")
                st.write(entry["summary"])
            with meta_col:
                compare_checked = st.checkbox(
                    "加入对比",
                    value=selected_for_compare,
                    key=f"compare_toggle_{entry['cache_key']}",
                )
                if compare_checked and not selected_for_compare:
                    st.session_state.compare_keys.append(entry["cache_key"])
                elif not compare_checked and selected_for_compare:
                    st.session_state.compare_keys = [k for k in st.session_state.compare_keys if k != entry["cache_key"]]

                if st.button("设为主论文", key=f"active_btn_{entry['cache_key']}", use_container_width=True):
                    st.session_state.active_paper_key = entry["cache_key"]
                    st.success("已设为主论文")
                if st.button("查看分析流", key=f"flow_btn_{entry['cache_key']}", use_container_width=True):
                    st.session_state.active_paper_key = entry["cache_key"]
                    goto_workspace("analysis")

            detail_tab1, detail_tab2, detail_tab3 = st.tabs(["卡片详情", "追溯与质量", "结果查看"])
            with detail_tab1:
                st.markdown(f"**作者**：{'、'.join(entry.get('authors', [])[:8]) or '未提取'}")
                if entry.get("method_tags"):
                    st.markdown("**方法标签**：" + " / ".join(entry["method_tags"]))
                if entry.get("dataset_tags"):
                    st.markdown("**数据标签**：" + " / ".join(entry["dataset_tags"]))
                if entry.get("innovation_points"):
                    st.markdown("**创新点**")
                    for item in entry["innovation_points"][:5]:
                        st.write(f"- {item}")
                if entry.get("limitations"):
                    st.markdown("**局限性**")
                    for item in entry["limitations"][:5]:
                        st.write(f"- {item}")
            with detail_tab2:
                st.write(f"来源：`{entry.get('original_source', 'N/A')}`")
                st.write(f"缓存键：`{entry['cache_key']}`")
                st.write(f"分析时间：{time.strftime('%Y-%m-%d %H:%M', time.localtime(entry['timestamp']))}")
                st.write(f"可靠性评分：{entry.get('reliability', '未生成')}")
                if entry.get("audit_metrics"):
                    st.json(entry["audit_metrics"])
            with detail_tab3:
                view_mode = st.radio(
                    "查看格式",
                    ["Markdown", "Structured JSON"],
                    key=f"view_mode_{entry['cache_key']}",
                    horizontal=True,
                )
                if view_mode == "Markdown":
                    st.markdown(entry.get("content") or "暂无 Markdown 结果")
                else:
                    st.json(entry.get("structured_data") or {"message": "暂无结构化结果"})


def render_single_paper_detail(active_entry: Optional[Dict[str, Any]]) -> None:
    if not active_entry:
        st.info("请先从论文库中选择一篇主论文。")
        return
    st.subheader(f"当前主论文：{active_entry['title']}")
    st.caption(f"{active_entry['year']} · {active_entry['venue']} · {active_entry['prompt_name']}")
    tab1, tab2, tab3 = st.tabs(["分析结果", "结构化卡片", "追问"])
    with tab1:
        st.markdown(active_entry.get("content") or "暂无分析结果")
    with tab2:
        st.json(active_entry.get("structured_data") or {"message": "暂无结构化结果"})
    with tab3:
        for msg in st.session_state.qa_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if prompt := st.chat_input("围绕当前主论文继续追问..."):
            st.session_state.qa_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                service = PaperAnalysisService(load_config())
                with st.spinner("正在生成回答..."):
                    response = service.ask_question(active_entry["cache_key"], prompt)
                st.markdown(response)
                st.session_state.qa_messages.append({"role": "assistant", "content": response})


def render_compare_panel(compare_entries: List[Dict[str, Any]]) -> None:
    st.subheader("跨论文对比")
    panel_state = compare_panel_state(compare_entries)
    if not panel_state["is_ready"]:
        st.warning(panel_state["warning"])
        return
    st.write("当前对比集合：")
    for title in panel_state["titles"]:
        st.write(f"- {title}")

    review_type = st.radio(
        "输出类型",
        ["横向对比矩阵", "技术演化梳理", "研究空白发现"],
        horizontal=True,
    )
    if st.button("执行跨论文分析", type="primary"):
        service = MultiPaperService(load_config())
        with st.spinner("正在生成综合报告..."):
            if review_type == "横向对比矩阵":
                report = service.compare_papers([e["cache_key"] for e in compare_entries])
            elif review_type == "技术演化梳理":
                report = service.trace_evolution([e["cache_key"] for e in compare_entries])
            else:
                report = service.discover_gaps([e["cache_key"] for e in compare_entries])
        st.markdown(report)
        st.download_button("下载报告", report, file_name=f"smartpaper_review_{int(time.time())}.md")


def render_research_map_panel(active_entry: Optional[Dict[str, Any]], entries: List[Dict[str, Any]], compare_entries: List[Dict[str, Any]]) -> None:
    st.subheader("研究映射")

    # 视图模式选择
    view_mode = st.radio(
        "视图模式",
        options=["Vue 交互式图谱", "简化统计"],
        horizontal=True,
        key="research_map_view_mode"
    )

    scope_entries = research_map_scope(entries, active_entry, compare_entries)
    if not scope_entries:
        st.info("暂无可用于映射的论文。")
        return

    # Vue 交互式图谱模式
    if view_mode == "Vue 交互式图谱":
        try:
            # 启动 API 服务器
            from infrastructure.research_map_api import start_api_server
            api_server = start_api_server(host="127.0.0.1", port=8001)
            st.success("🚀 研究地图 API 服务已启动")

            # 构造论文缓存键列表
            cache_keys = [entry["cache_key"] for entry in scope_entries if "cache_key" in entry]

            # 显示 Vue 组件
            vue_html = f"""
            <div id="smartpaper-research-map" style="width:100%;height:700px;">
                <iframe
                    src="http://127.0.0.1:5173?cacheKeys={','.join(cache_keys)}"
                    width="100%"
                    height="700px"
                    style="border:none;border-radius:8px;"
                    frameborder="0">
                </iframe>
            </div>
            """
            st.components.v1.html(vue_html, height=750, scrolling=False)

            st.info("💡 提示：如果 Vue 图谱无法加载，请确保已启动 Vue 开发服务器（cd vue-frontend && npm run dev）")

        except Exception as e:
            st.error(f"Vue 图谱加载失败: {e}")
            st.info("回退到简化统计模式")

    # 简化统计模式（原有逻辑）
    if view_mode == "简化统计":
        years: Dict[str, int] = {}
        method_tags: Dict[str, int] = {}
        dataset_tags: Dict[str, int] = {}
        app_tags: Dict[str, int] = {}
        for entry in scope_entries:
            years[str(entry.get("year", "未知"))] = years.get(str(entry.get("year", "未知")), 0) + 1
            for tag in entry.get("method_tags", []):
                method_tags[tag] = method_tags.get(tag, 0) + 1
            for tag in entry.get("dataset_tags", []):
                dataset_tags[tag] = dataset_tags.get(tag, 0) + 1
            for tag in entry.get("application_tags", []):
                app_tags[tag] = app_tags.get(tag, 0) + 1
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**时间线分布**")
            st.json(dict(sorted(years.items())))
            st.markdown("**方法主题**")
            st.json(dict(sorted(method_tags.items(), key=lambda x: x[1], reverse=True)[:12]))
        with col2:
            st.markdown("**数据主题**")
            st.json(dict(sorted(dataset_tags.items(), key=lambda x: x[1], reverse=True)[:12]))
            st.markdown("**应用主题**")
            st.json(dict(sorted(app_tags.items(), key=lambda x: x[1], reverse=True)[:12]))

    if active_entry:
        st.markdown("---")
        st.markdown("**主论文与科研画像的相关性评估**")
        if st.button("生成主论文相关性报告", use_container_width=True):
            service = PaperAnalysisService(load_config())
            with st.spinner("正在评估相关性..."):
                result = service.calculate_relevance(active_entry["cache_key"])
            if "error" in result:
                st.error(result["error"])
                if result.get("raw_content"):
                    st.code(result["raw_content"])
            else:
                score_col, desc_col = st.columns([0.25, 0.75])
                score_col.metric("相关度", f"{result.get('relevance_score', 0)}%")
                with desc_col:
                    st.markdown("**匹配点**")
                    for item in result.get("matching_points", []):
                        st.write(f"- {item}")
                    st.markdown("**差异/空白**")
                    for item in result.get("gap_points", []):
                        st.write(f"- {item}")
                    st.markdown("**应用建议**")
                    st.write(result.get("usage_suggestion", "暂无建议"))


def render_analysis_workspace(entries: List[Dict[str, Any]]) -> None:
    st.header("🧠 分析工作流")
    st.caption("围绕\"主论文 + 对比集合\"组织单篇查看、跨论文对比、研究映射与追问。")

    # 添加论文选择区域
    if entries:
        st.markdown("---")
        st.subheader("📋 快速选择论文")

        # 主论文选择
        entry_options = {f"{e['title']} ({e['year']})": e["cache_key"] for e in entries}
        active_key = st.session_state.get("active_paper_key")
        if active_key not in entry_options.values():
            active_key = None

        selected_title = st.selectbox(
            "选择主论文",
            options=list(entry_options.keys()),
            index=list(entry_options.values()).index(active_key) if active_key else 0,
            key="main_paper_selector"
        )

        if selected_title:
            selected_key = entry_options[selected_title]
            if selected_key != st.session_state.active_paper_key:
                st.session_state.active_paper_key = selected_key
                st.rerun()

        # 对比论文多选
        compare_titles = st.multiselect(
            "选择对比论文（可多选）",
            options=list(entry_options.keys()),
            default=[k for k, v in entry_options.items() if v in st.session_state.compare_keys],
            key="compare_papers_selector"
        )

        # 更新对比集合
        new_compare_keys = [entry_options[title] for title in compare_titles]
        if new_compare_keys != st.session_state.compare_keys:
            st.session_state.compare_keys = new_compare_keys
            st.rerun()

        st.markdown("---")
    else:
        st.info("📚 论文库暂无论文，请先前往\"导入与解析\"添加论文。")

    active_entry = get_entry_by_key(st.session_state.active_paper_key, entries)
    compare_entries = [entry for entry in entries if entry["cache_key"] in st.session_state.compare_keys]
    tab1, tab2, tab3 = st.tabs(["单篇工作台", "跨论文对比", "研究映射"])
    with tab1:
        render_single_paper_detail(active_entry)
    with tab2:
        render_compare_panel(compare_entries)
    with tab3:
        render_research_map_panel(active_entry, entries, compare_entries)


def render_zotero_workspace() -> None:
    st.header("🗂️ Zotero 集成")
    st.caption("当前先提供统一入口、导入映射配置和批次追踪；待后端接口接入后，这里将直接切换为真实同步视图。")

    left, right = st.columns([0.45, 0.55])
    with left:
        st.subheader("连接与映射配置")
        st.text_input("Zotero API Key", value="", type="password", placeholder="后端接入后使用")
        st.text_input("User / Group ID", placeholder="例如 userId 或 groupId")
        st.selectbox("库类型", ["个人库", "团队库"])
        st.multiselect("同步内容", ["条目", "附件", "标签", "Collections"], default=["条目", "附件", "标签"])
        st.checkbox("导入后自动进入论文库", value=True)
        st.checkbox("保留 Zotero collection 路径", value=True)
        st.info("当前仓库尚未提供 Zotero 基础设施实现，因此此页不会发起真实同步请求。")

    with right:
        st.subheader("已记录批次")
        if not st.session_state.zotero_batches:
            st.info("暂无 Zotero 导入批次，请在“导入与解析”页面记录。")
        else:
            for idx, batch in enumerate(st.session_state.zotero_batches, start=1):
                with st.container(border=True):
                    st.markdown(f"**批次 {idx} · {batch['library']}**")
                    st.caption(f"{batch['timestamp']} · {batch['mapping_mode']} · {batch['status']}")
                    if batch.get("files"):
                        st.write("文件：" + ", ".join(batch["files"]))


def main() -> None:
    st.set_page_config(page_title="SmartPaper Workbench", layout="wide")

    # ============================================
    # 完整的现代化 CSS 样式系统
    # ============================================
    st.markdown(
        """
        <style>
        /* ==================== CSS 变量定义 ==================== */
        :root {
            /* 主色调 - 专业学术蓝 */
            --primary-color: #1e40af;
            --primary-hover: #1e3a8a;
            --primary-light: #dbeafe;
            --primary-dark: #1e3a8a;

            /* 辅助色系 */
            --secondary-color: #0891b2;
            --secondary-light: #cffafe;
            --accent-color: #7c3aed;
            --accent-light: #ede9fe;

            /* 语义颜色 */
            --success-color: #059669;
            --success-light: #d1fae5;
            --warning-color: #d97706;
            --warning-light: #fef3c7;
            --error-color: #dc2626;
            --error-light: #fee2e2;
            --info-color: #0891b2;
            --info-light: #ecfeff;

            /* 背景色 */
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --bg-card: #ffffff;
            --bg-hover: #f0f9ff;

            /* 文字颜色 */
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-tertiary: #64748b;
            --text-light: #94a3b8;

            /* 边框颜色 */
            --border-color: #e2e8f0;
            --border-hover: #cbd5e1;
            --border-focus: #3b82f6;

            /* 阴影 */
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

            /* 圆角 */
            --radius-sm: 4px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
            --radius-2xl: 24px;

            /* 间距 */
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --spacing-2xl: 48px;
        }

        /* ==================== 全局样式 ==================== */
        /* 使用更具体的选择器来减少 !important */
        [data-testid="stAppViewBlockContainer"] > div > div > div > div > div.block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        .main .block-container {
            background: linear-gradient(135deg, var(--bg-secondary) 0%, #f1f8ff 100%);
            border-radius: 0;
        }

        /* 滚动条美化 */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: var(--bg-tertiary);
            border-radius: var(--radius-md);
        }
        ::-webkit-scrollbar-thumb {
            background: var(--text-light);
            border-radius: var(--radius-md);
            transition: background 0.3s ease;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-tertiary);
        }

        /* ==================== 标题排版 ==================== */
        /* 使用更具体的选择器，减少 !important */
        .main h1,
        [data-testid="stHeader"] h1 {
            color: var(--primary-dark);
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: var(--spacing-lg);
            letter-spacing: -0.025em;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }

        .main h2 {
            color: var(--primary-color);
            font-size: 1.875rem;
            font-weight: 600;
            margin-top: var(--spacing-xl);
            margin-bottom: var(--spacing-md);
            border-bottom: 2px solid var(--primary-light);
            padding-bottom: var(--spacing-sm);
        }

        .main h3 {
            color: var(--primary-hover);
            font-size: 1.5rem;
            font-weight: 600;
            margin-top: var(--spacing-lg);
            margin-bottom: var(--spacing-sm);
        }

        .main h4 {
            color: var(--text-primary);
            font-size: 1.25rem;
            font-weight: 600;
            margin-top: var(--spacing-md);
            margin-bottom: var(--spacing-xs);
        }

        /* ==================== 文字样式 ==================== */
        .main p,
        .main li,
        .main td,
        .main th {
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.7;
        }

        /* ==================== 侧边栏样式 ==================== */
        /* 使用更具体的层级选择器 */
        section[data-testid="stSidebar"] > div:nth-child(1) {
            background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary-color) 100%);
            box-shadow: var(--shadow-lg);
            color: white;
        }

        section[data-testid="stSidebar"] > div:nth-child(1) > div {
            background: transparent;
        }

        /* 侧边栏标题 */
        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            color: white;
            font-weight: 600;
        }

        /* 侧边导航按钮 */
        section[data-testid="stSidebar"] button[kind="primary"],
        section[data-testid="stSidebar"] button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: var(--radius-md);
            padding: var(--spacing-sm) var(--spacing-md);
            margin-bottom: var(--spacing-xs);
            transition: all 0.3s ease;
            text-align: left;
            font-weight: 500;
        }

        section[data-testid="stSidebar"] button[kind="primary"]:hover,
        section[data-testid="stSidebar"] button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.2);
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }

        /* 侧边栏输入框 */
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] select {
            background: rgba(255, 255, 255, 0.95);
            border-radius: var(--radius-md);
            color: #1e293b !important;
        }

        /* 输入框内的占位符文字 */
        section[data-testid="stSidebar"] input::placeholder,
        section[data-testid="stSidebar"] textarea::placeholder {
            color: #94a3b8 !important;
        }

        /* Selectbox 下拉选项文字 - 使用更高优先级的选择器 */
        section[data-testid="stSidebar"] [data-baseweb="select"] [role="listbox"],
        section[data-testid="stSidebar"] [data-baseweb="select"] [role="option"] {
            color: #1e293b !important;
            background-color: #ffffff !important;
        }

        /* 侧边栏标签和说明文字 - 确保对比度 */
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] caption {
            color: #ffffff !important;
        }

        /* 侧边栏通用文字 - 排除输入框和下拉选项内的文字 */
        section[data-testid="stSidebar"] > div > div > div > div > div > span:not(input + span):not(.stSelectbox span):not(.stMultiSelect span):not(.stFileUploader span) {
            color: #ffffff !important;
        }

        /* 侧边栏通用 div - 排除输入框和下拉选项容器 */
        section[data-testid="stSidebar"] > div > div > div > div > div:not(:has(input)):not(:has(select)):not(:has(textarea)) {
            color: #ffffff !important;
        }

        /* 确保输入框容器内的 div 文字不会被覆盖 */
        section[data-testid="stSidebar"] input + div,
        section[data-testid="stSidebar"] select + div,
        section[data-testid="stSidebar"] textarea + div {
            color: #1e293b !important;
        }

        /* 侧边栏链接文字 */
        section[data-testid="stSidebar"] a {
            color: #e0e7ff !important;
        }

        /* 侧边栏 checkbox 标签 */
        section[data-testid="stSidebar"] .stCheckbox label {
            color: #ffffff !important;
        }

        /* 侧边栏 radio/selectbox 标签 */
        section[data-testid="stSidebar"] .stRadio label,
        section[data-testid="stSidebar"] .stSelectbox label {
            color: #ffffff !important;
        }

        /* 侧边栏 radio 选项文字 */
        section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label {
            color: #f5f5f5 !important;
        }

        /* 侧边栏 caption 文字 */
        section[data-testid="stSidebar"] caption {
            color: #e0e0e0 !important;
        }

        /* 侧边栏 progress 文字 */
        section[data-testid="stSidebar"] .stProgress label {
            color: #ffffff !important;
        }

        /* 侧边栏 expander 标题 */
        section[data-testid="stSidebar"] .streamlit-expanderHeader {
            color: #ffffff !important;
        }

        /* 侧边栏 expander 内容 */
        section[data-testid="stSidebar"] .streamlit-expanderContent {
            color: #f5f5f5 !important;
        }

        /* 侧边栏 subheader */
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] h4,
        section[data-testid="stSidebar"] h5 {
            color: #ffffff !important;
        }

        /* ==================== 按钮样式 ==================== */
        /* 主按钮 - 使用更具体的选择器减少 !important */
        button[kind="primary"] {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
            color: white;
            border: none;
            border-radius: var(--radius-md);
            padding: var(--spacing-sm) var(--spacing-lg);
            font-weight: 600;
            box-shadow: var(--shadow-md);
            transition: all 0.3s ease;
            letter-spacing: 0.025em;
        }

        button[kind="primary"]:hover {
            background: linear-gradient(135deg, var(--primary-hover) 0%, var(--primary-dark) 100%);
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
        }

        button[kind="primary"]:active {
            transform: translateY(0);
        }

        /* 次要按钮 */
        button[kind="secondary"] {
            background: var(--bg-card);
            color: var(--primary-color);
            border: 2px solid var(--primary-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-sm) var(--spacing-lg);
            font-weight: 600;
            transition: all 0.3s ease;
        }

        button[kind="secondary"]:hover {
            background: var(--primary-light);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        /* ==================== 卡片容器样式 ==================== */
        /* 带边框的容器 - 优化选择器减少 !important */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            margin: var(--spacing-md) 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        div[data-testid="stVerticalBlockBorderWrapper"]:hover {
            border-color: var(--border-hover);
            box-shadow: var(--shadow-lg);
        }

        /* 容器内的标题 */
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div > h2,
        div[data-testid="stVerticalBlockBorderWrapper"] > div > div > h3 {
            background: var(--bg-tertiary);
            padding: var(--spacing-md) var(--spacing-lg);
            margin: 0;
            border-bottom: 1px solid var(--border-color);
            color: var(--primary-color);
        }

        /* Expander 美化 */
        .streamlit-expanderHeader {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md) var(--spacing-lg);
            font-weight: 600;
            color: var(--text-primary);
            transition: all 0.3s ease;
        }

        .streamlit-expanderHeader:hover {
            background: var(--bg-hover);
            border-color: var(--border-focus);
        }

        .streamlit-expanderContent {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-top: none;
            border-radius: 0 0 var(--radius-md) var(--radius-md);
            padding: var(--spacing-lg);
        }

        /* ==================== 进度条样式 ==================== */
        [data-testid="stProgress"] > div > div > div {
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            transition: width 0.5s ease;
        }

        [data-testid="stProgress"] > div > div {
            background: var(--bg-tertiary);
            border-radius: var(--radius-lg);
            overflow: hidden;
        }

        /* ==================== 文件上传区域 ==================== */
        [data-testid="stFileUploader"] {
            border: 2px dashed var(--border-color);
            border-radius: var(--radius-xl);
            padding: var(--spacing-2xl);
            background: var(--bg-secondary);
            transition: all 0.3s ease;
        }

        [data-testid="stFileUploader"]:hover {
            border-color: var(--primary-color);
            background: var(--primary-light);
        }

        [data-testid="stFileUploader"] p {
            color: var(--text-tertiary);
        }

        /* ==================== 输入框样式 ==================== */
        input[type="text"],
        input[type="url"],
        input[type="number"],
        textarea,
        select {
            background: var(--bg-card);
            border: 2px solid var(--border-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-sm) var(--spacing-md);
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus,
        input[type="url"]:focus,
        input[type="number"]:focus,
        textarea:focus,
        select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px var(--primary-light);
            outline: none;
        }

        /* ==================== Metric 卡片样式 ==================== */
        /* 问题 2 修复：为 Metric 组件添加特定样式选择器 */
        [data-testid="stMetric"] > div > div > div > div > div:nth-child(1) {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
        }

        [data-testid="stMetric"] > div > div > div > div > div:nth-child(2) {
            color: var(--text-tertiary);
            font-weight: 600;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* ==================== 数据表格样式 ==================== */
        table.dataframe {
            border: 1px solid var(--border-color);
            border-radius: var(--radius-lg);
            overflow: hidden;
            box-shadow: var(--shadow-sm);
        }

        table.dataframe th {
            background: var(--primary-dark);
            color: white;
            font-weight: 600;
            padding: var(--spacing-md) var(--spacing-lg);
            text-align: left;
        }

        table.dataframe td {
            background: var(--bg-card);
            border-bottom: 1px solid var(--border-color);
            padding: var(--spacing-md) var(--spacing-lg);
            transition: background 0.2s ease;
        }

        table.dataframe tr:hover td {
            background: var(--bg-hover);
        }

        /* ==================== 复选框和单选框 ==================== */
        [data-testid="stCheckbox"] label,
        [data-testid="stRadio"] label {
            color: var(--text-secondary);
            font-weight: 500;
            padding: var(--spacing-xs) var(--spacing-sm);
            transition: color 0.2s ease;
        }

        [data-testid="stCheckbox"] label:hover,
        [data-testid="stRadio"] label:hover {
            color: var(--primary-color);
        }

        /* ==================== 代码块样式 ==================== */
        pre {
            background: #1e293b;
            color: #e2e8f0;
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-md);
        }

        code {
            background: var(--bg-tertiary);
            color: var(--primary-color);
            padding: 2px 6px;
            border-radius: var(--radius-sm);
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
        }

        /* ==================== 状态标签样式（用于 st.info / st.success 等） ==================== */
        /* Streamlit 原生消息框样式增强 */
        [data-testid="stInfo"] {
            background: var(--info-light);
            border-left: 4px solid var(--info-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md) var(--spacing-lg);
        }
        [data-testid="stInfo"] p {
            color: var(--info-color);
            font-weight: 500;
        }

        [data-testid="stSuccess"] {
            background: var(--success-light);
            border-left: 4px solid var(--success-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md) var(--spacing-lg);
        }
        [data-testid="stSuccess"] p {
            color: var(--success-color);
            font-weight: 500;
        }

        [data-testid="stWarning"] {
            background: var(--warning-light);
            border-left: 4px solid var(--warning-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md) var(--spacing-lg);
        }
        [data-testid="stWarning"] p {
            color: var(--warning-color);
            font-weight: 500;
        }

        [data-testid="stError"] {
            background: var(--error-light);
            border-left: 4px solid var(--error-color);
            border-radius: var(--radius-md);
            padding: var(--spacing-md) var(--spacing-lg);
        }
        [data-testid="stError"] p {
            color: var(--error-color);
            font-weight: 500;
        }

        /* ==================== 加载动画 ==================== */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        /* ==================== 分割线样式 ==================== */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--border-color), transparent);
            margin: var(--spacing-xl) 0;
        }

        /* ==================== Tab 样式 ==================== */
        /* Tab 组件需要使用 !important 因为 Streamlit 内联样式特异性很高 */
        [data-testid="stTabs"] > [role="tablist"] {
            background: var(--bg-tertiary) !important;
            border-radius: var(--radius-md) !important;
            padding: var(--spacing-xs) !important;
            gap: var(--spacing-xs) !important;
        }

        [data-testid="stTabs"] [role="tab"] {
            background: transparent !important;
            border: none !important;
            color: var(--text-secondary) !important;
            font-weight: 600 !important;
            padding: var(--spacing-sm) var(--spacing-lg) !important;
            border-radius: var(--radius-sm) !important;
            transition: all 0.3s ease !important;
        }

        [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
            background: var(--bg-card) !important;
            color: var(--primary-color) !important;
            box-shadow: var(--shadow-sm);
        }

        [data-testid="stTabs"] [role="tab"]:hover {
            background: var(--primary-light) !important;
        }

        [data-testid="stTabs"] [data-testid="stTabContent"] {
            background: var(--bg-card) !important;
            border: 1px solid var(--border-color) !important;
            border-top: none !important;
            border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
            padding: var(--spacing-xl) !important;
        }

        /* ==================== 响应式设计 ==================== */
        @media (max-width: 768px) {
            .main h1 { font-size: 2rem; }
            .main h2 { font-size: 1.5rem; }
            .main h3 { font-size: 1.25rem; }

            [data-testid="stAppViewBlockContainer"] > div > div > div > div > div.block-container {
                padding-top: 1rem;
                padding-bottom: 2rem;
            }
        }

        /* ==================== 特殊效果 ==================== */
        .glow-effect {
            box-shadow: 0 0 20px rgba(30, 64, 175, 0.3);
        }

        .fade-in {
            animation: fadeIn 0.5s ease-in;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ==================== 修复侧边栏 selectbox 选项文字 ==================== */
        /* 确保侧边栏 selectbox 的下拉选项文字是深色 */
        section[data-testid="stSidebar"] [role="listbox"] div,
        section[data-testid="stSidebar"] [role="listbox"] span,
        section[data-testid="stSidebar"] [role="option"] div,
        section[data-testid="stSidebar"] [role="option"] span {
            color: #1e293b !important;
            background: white !important;
        }

        /* 确保侧边栏 selectbox 展开后的容器背景 */
        section[data-testid="stSidebar"] [role="listbox"] {
            background: white !important;
        }

        /* 确保侧边栏所有输入组件内的文字都是深色 */
        section[data-testid="stSidebar"] input,
        section[data-testid="stSidebar"] textarea,
        section[data-testid="stSidebar"] select {
            color: #1e293b !important;
        }

        /* 确保侧边栏 selectbox 选中项的文字 */
        section[data-testid="stSidebar"] [aria-selected="true"],
        section[data-testid="stSidebar"] [data-selected="true"] {
            color: #1e293b !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title("赋睿科研工作台 🚀")
    init_session_state()
    options = get_available_options()
    workbench_service = WorkbenchService()
    entries = workbench_service.list_library_entries()
    config = render_sidebar(options, entries, workbench_service)

    workspace = st.session_state.workspace
    if workspace == "overview":
        render_overview(entries)
    elif workspace == "intake":
        render_import_workspace(config)
    elif workspace == "library":
        render_library_workspace(entries)
    elif workspace == "analysis":
        render_analysis_workspace(entries)
    elif workspace == "zotero":
        render_zotero_workspace()


if __name__ == "__main__":
    main()
