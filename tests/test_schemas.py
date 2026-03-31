from domain.schemas import StructuredAnalysisData
import json

data = {
    "paper_id": "test_id",
    "source": {"type": "pdf", "path": "/path/to/pdf.pdf"},
    "analysis": {
        "summary_one_sentence": "Test short summary"
    }
}

try:
    obj = StructuredAnalysisData(**data)
    print("Schema initialized successfully:")
    print(obj.model_dump_json(indent=2))
except Exception as e:
    print("Error initializing schema:", e)
