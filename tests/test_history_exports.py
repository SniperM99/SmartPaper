import sys
import os
sys.path.insert(0, '/Users/m99/Documents/SmartPaper/src')
sys.path.insert(0, '/Users/m99/Documents/SmartPaper')
from core.history_manager import HistoryManager
from domain.schemas import StructuredAnalysisData

# Ensure temp dir exists
os.makedirs('/Users/m99/Documents/SmartPaper/temp/test_analyses', exist_ok=True)

hm = HistoryManager(storage_dir="temp/test_analyses")
data = {
    "paper_id": "test_export_123",
    "metadata": {"title": "Test Title", "year": "2026", "venue": "Test Venue", "keywords": ["k1", "k2"]},
    "analysis": {"research_problem": "Test Problem", "summary_one_sentence": "Test Summary"},
    "trace": {"analysis_time": "1.23s"}
}
obj = StructuredAnalysisData(**data)

hm.save_analysis(source="test.pdf", source_hash="abcdef12", prompt_name="default", content="# Test MD Content", structured_data=obj.model_dump())

files = os.listdir("/Users/m99/Documents/SmartPaper/temp/test_analyses")
print("Files created:")
for f in files:
    print(f)
