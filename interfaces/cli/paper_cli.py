"""论文分析命令行接口"""

import argparse
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, '/Users/m99/Documents/SmartPaper')
sys.path.insert(0, '/Users/m99/Documents/SmartPaper/src')

from application.paper_analysis_service import PaperAnalysisService
from core.prompt_manager import get_available_options
from core.config_loader import load_config


def cmd_analyze(args):
    """分析单个论文"""
    config = load_config(args.config)
    service = PaperAnalysisService(config)

    if args.url:
        result = service.analyze_url(
            args.url, 
            role=args.role, 
            task=args.task or args.prompt or "summarization", 
            domain=args.domain, 
            use_chain=args.chain
        )
    else:
        result = service.analyze_file(
            args.file, 
            role=args.role, 
            task=args.task or args.prompt or "summarization", 
            domain=args.domain, 
            use_chain=args.chain
        )

    print("\n" + "="*60)
    print(result.content)
    print("="*60)


def cmd_analyze_stream(args):
    """流式分析论文"""
    config = load_config(args.config)
    service = PaperAnalysisService(config)

    task = args.task or args.prompt or "summarization"
    if args.url:
        for chunk in service.analyze_url_stream(args.url, role=args.role, task=task, domain=args.domain):
            print(chunk, end='', flush=True)
    else:
        for chunk in service.analyze_stream(args.file, role=args.role, task=task, domain=args.domain):
            print(chunk, end='', flush=True)
    print()


def cmd_batch(args):
    """批量分析"""
    config = load_config(args.config)
    service = PaperAnalysisService(config)

    # 查找所有 PDF 文件
    dir_path = Path(args.directory)
    if not dir_path.exists():
        print(f"错误: 目录不存在 {dir_path}")
        return

    if args.recursive:
        pdf_files = [str(f) for f in dir_path.rglob("*.pdf")]
    else:
        pdf_files = [str(f) for f in dir_path.glob("*.pdf")]

    if not pdf_files:
        print("未找到 PDF 文件")
        return

    print(f"正在启动批量分析任务 (共 {len(pdf_files)} 个文件)...")
    stats = service.process_batch(
        pdf_files, 
        role=args.role,
        task=args.task or args.prompt or "summarization",
        domain=args.domain,
        use_chain=args.chain,
        resume=args.resume,
        overwrite=args.overwrite
    )

    print(f"\n" + "="*40)
    print(f"📊 批量分析任务完成报告")
    print(f"="*40)
    print(f"  📅 总计任务数: {stats['total']}")
    print(f"  ✅ 成功处理:   {stats['completed']}")
    print(f"  ❌ 处理失败:   {stats['failed']}")
    print(f"  ⏳ 待处理:     {stats['pending']}")
    print(f"  ⏱️ 总计耗时:   {stats['total_duration']:.2f} 秒")
    print(f"  ⏲️ 平均耗时:   {stats['total_duration']/stats['completed']:.2f} 秒/篇" if stats['completed'] > 0 else "")
    print(f"  🪙 总计 Token: {stats['total_tokens']}")
    print(f"="*40)
    if stats['failed'] > 0:
        print("💡 提示: 您可以检查失败原因并使用 --resume 重新运行。")


def cmd_list_prompts(args):
    """列出所有可用的提示词选项"""
    options = get_available_options()
    
    print("\n🎭 可用角色 (Roles):")
    for name, desc in options["roles"].items():
        print(f"  {name:20} - {desc}")
        
    print("\n📋 可用任务 (Tasks):")
    for name, desc in options["tasks"].items():
        print(f"  {name:20} - {desc}")
        
    print("\n🌐 可用领域 (Domains):")
    for name, desc in options["domains"].items():
        print(f"  {name:20} - {desc}")
        
    print("\n💾 预设模板 (Presets):")
    for name, desc in options["prompts"].items():
        print(f"  {name:20} - {desc}")


def cmd_export(args):
    """导出分析结果"""
    hm = HistoryManager()
    analysis = hm.get_analysis(args.id)
    if not analysis:
        print(f"❌ 找不到 ID 为 {args.id} 的记录")
        return
        
    output_path = Path(args.output or f"export_{args.id}.{args.format}")
    if args.format == "json":
        import json
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
    else:
        content = analysis.get("content", "无内容")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"✅ 成功导出到 {output_path}")

def cmd_compare(args):
    """对比多个论文"""
    config = load_config(args.config)
    ms = MultiPaperService(config)
    print(f"🧐 正在对 {len(args.ids)} 篇论文进行对比分析...")
    
    if args.mode == "matrix":
        report = ms.compare_papers(args.ids)
    elif args.mode == "evolution":
        report = ms.trace_evolution(args.ids)
    elif args.mode == "gaps":
        report = ms.discover_gaps(args.ids)
    else:
        report = ms.render_research_map(args.ids)
        
    print("\n" + "="*60)
    print(report)
    print("="*60)

def cmd_search(args):
    """在本地库中搜索"""
    hm = HistoryManager()
    history = hm.list_history()
    results = [e for e in history if args.query.lower() in e['file_name'].lower() or args.query.lower() in e['cache_key'].lower()]
    
    if not results:
        print(f"🔍 未找到包含 '{args.query}' 的记录")
        return
        
    print(f"🔍 找到 {len(results)} 条匹配记录:")
    print("-" * 60)
    for r in results:
        print(f"ID: {r['cache_key'][:8]}... | Name: {r['file_name'][:30]:30} | Task: {r.get('prompt_name', 'N/A')}")
    print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description='SmartPaper 专业科研集成工具')
    parser.add_argument('--config', '-c', default='config/config.yaml', help='配置文件路径')
    
    subparsers = parser.add_subparsers(dest='command', help='核心命令')

    # Analyze Group
    analyze_parser = subparsers.add_parser('analyze', help='分析任务')
    analyze_sub = analyze_parser.add_subparsers(dest='subcommand')
    
    # Analyze File
    f_p = analyze_sub.add_parser('file', help='解析本地文件')
    f_p.add_argument('path', help='文件路径')
    f_p.add_argument('--role', default='general_assistant')
    f_p.add_argument('--task', '-t', default='summarization')
    f_p.set_defaults(func=lambda args: cmd_analyze(argparse.Namespace(config=args.config, file=args.path, url=None, role=args.role, task=args.task, domain='general', chain=False)))

    # Analyze Folder
    dir_p = analyze_sub.add_parser('folder', help='批量解析目录')
    dir_p.add_argument('directory', help='目录路径')
    dir_p.add_argument('--recursive', '-r', action='store_true')
    dir_p.set_defaults(func=lambda args: cmd_batch(argparse.Namespace(config=args.config, directory=args.directory, recursive=args.recursive, role='general_assistant', task='summarization', domain='general', chain=False, resume=True, overwrite=False)))

    # Export
    export_p = subparsers.add_parser('export', help='导出记录')
    export_p.add_argument('id', help='记录 ID')
    export_p.add_argument('--format', choices=['json', 'md'], default='md')
    export_p.add_argument('--output', '-o', help='输出路径')
    export_p.set_defaults(func=cmd_export)

    # Compare
    compare_p = subparsers.add_parser('compare', help='多论文对比')
    compare_p.add_argument('ids', nargs='+', help='记录 ID 列表')
    compare_p.add_argument('--mode', choices=['matrix', 'evolution', 'gaps', 'map'], default='matrix')
    compare_p.set_defaults(func=cmd_compare)

    # Search
    search_p = subparsers.add_parser('search', help='搜索本地库')
    search_p.add_argument('query', help='搜索关键词')
    search_p.set_defaults(func=cmd_search)

    # Prompts
    prompts_p = subparsers.add_parser('prompts', help='列出所有模板')
    prompts_p.set_defaults(func=cmd_list_prompts)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    if hasattr(args, 'func'):
        args.func(args)

if __name__ == '__main__':
    main()
