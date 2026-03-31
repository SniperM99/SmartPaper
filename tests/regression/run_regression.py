"""
SmartPaper 回归测试集
用于验证核心分析功能在更新后的稳定性。
"""

import os
import sys
import yaml
import json
import time
from typing import Dict, List, Any
from loguru import logger

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from application.paper_analysis_service import PaperAnalysisService
from core.config_loader import load_config

class RegressionRunner:
    def __init__(self, plan_path: str):
        self.config = load_config()
        self.service = PaperAnalysisService(self.config)
        
        with open(plan_path, 'r', encoding='utf-8') as f:
            self.plan = yaml.safe_load(f)
            
        self.results = []

    def run_all(self):
        logger.info(f"🚀 开始执行回归测试，共 {len(self.plan['tests'])} 个用例")
        
        for test_case in self.plan['tests']:
            logger.info(f"正在测试: {test_case['name']}")
            result = self.run_test_case(test_case)
            self.results.append(result)
            
        self.report()

    def run_test_case(self, case: Dict) -> Dict:
        file_path = case['file_path']
        # 补全绝对路径
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getcwd(), file_path)
            
        if not os.path.exists(file_path):
            return {"case": case['name'], "status": "FAILED", "error": f"文件不存在: {file_path}"}
            
        try:
            start_t = time.time()
            # 执行分析 (强制不使用缓存以便测试 LLM)
            # 注意：PaperAnalysisService 的 analyze_file 目前会自动检查缓存
            # 如果要真实测试 LLM，可以考虑临时清空缓存或在 Service 中加开关
            analysis = self.service.analyze_file(file_path, overwrite=True)
            duration = time.time() - start_t
            
            # 验证结果
            errors = self.validate(analysis, case['expected'])
            
            return {
                "case": case['name'],
                "status": "PASSED" if not errors else "FAILED",
                "duration": round(duration, 2),
                "metrics": analysis.get("audit_metrics", {}),
                "errors": errors
            }
        except Exception as e:
            logger.exception(f"测试用例 {case['name']} 执行出错")
            return {"case": case['name'], "status": "ERROR", "error": str(e)}

    def validate(self, analysis: Dict, expected: Dict) -> List[str]:
        errors = []
        struct = analysis.get("structured_data", {})
        meta = struct.get("metadata", {})
        analysis_block = struct.get("analysis", {})
        
        # 1. 标题包含
        if "title_contains" in expected:
            title = meta.get("title", "")
            if expected["title_contains"].lower() not in title.lower():
                errors.append(f"标题验证失败: 期望包含 '{expected['title_contains']}', 实际为 '{title}'")
                
        # 2. 关键词匹配
        if "keywords" in expected:
            found_keywords = [k.lower() for k in meta.get("keywords", [])]
            for ek in expected["keywords"]:
                if ek.lower() not in found_keywords:
                    errors.append(f"关键词缺失: {ek}")
                    
        # 3. 摘要长度
        if "min_summary_length" in expected:
            summary = analysis_block.get("summary_one_sentence", "")
            if len(summary) < expected["min_summary_length"]:
                errors.append(f"摘要太短: {len(summary)} < {expected['min_summary_length']}")
                
        # 4. 创新点数量
        if "min_innovation_points" in expected:
            points = analysis_block.get("innovation_points", [])
            if len(points) < expected["min_innovation_points"]:
                errors.append(f"创新点不足: {len(points)} < {expected['min_innovation_points']}")
                
        return errors

    def report(self):
        print("\n" + "="*50)
        print("📊 回归测试报告")
        print("="*50)
        
        passed = sum(1 for r in self.results if r["status"] == "PASSED")
        total = len(self.results)
        
        for r in self.results:
            status_icon = "✅" if r["status"] == "PASSED" else "❌"
            print(f"{status_icon} {r['case']}: {r['status']} ({r.get('duration', 0)}s)")
            if r.get("errors"):
                for err in r["errors"]:
                    print(f"   - {err}")
            if r.get("error"):
                print(f"   - Error: {r['error']}")
                
        print("-" * 50)
        print(f"总计: {total} | 通过: {passed} | 失败: {total - passed}")
        print("="*50 + "\n")

if __name__ == "__main__":
    plan_file = os.path.join(os.path.dirname(__file__), "test_plan.yaml")
    runner = RegressionRunner(plan_file)
    runner.run_all()
