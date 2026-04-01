#!/usr/bin/env python3
"""测试后端模块导入"""
import sys

def test_imports():
    """测试所有模块是否可以正常导入"""
    print("🧪 测试后端模块导入...\n")

    modules = [
        "app.core.config",
        "app.core.logging",
        "app.models.requests",
        "app.models.responses",
        "app.services.analysis_service",
        "app.services.ingestion_service",
        "app.services.research_map_service",
        "app.services.zotero_service",
        "app.services.file_service",
        "app.services.profile_service",
        "app.api.routers.paper_analysis",
        "app.api.routers.literature_ingestion",
        "app.api.routers.research_map",
        "app.api.routers.zotero",
        "app.api.routers.file_ops",
        "app.api.routers.profile",
    ]

    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except Exception as e:
            print(f"❌ {module} - {e}")
            failed.append(module)

    print("\n" + "="*60)
    if failed:
        print(f"❌ 导入失败: {len(failed)} 个模块")
        for m in failed:
            print(f"   - {m}")
        return False
    else:
        print(f"✅ 所有模块导入成功 ({len(modules)} 个)")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
