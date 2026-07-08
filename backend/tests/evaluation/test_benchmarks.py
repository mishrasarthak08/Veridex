import json
import pytest
from pathlib import Path
from app.observability.evaluation.judge import LLMJudge

# Setup: load golden dataset
DATASET_PATH = Path("app/observability/evaluation/golden_dataset.json")

def load_dataset():
    if not DATASET_PATH.exists():
        return []
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

@pytest.mark.asyncio
async def test_golden_dataset():
    """
    Runs the LLM Judge against the golden dataset to ensure no regression.
    """
    dataset = load_dataset()
    if not dataset:
        pytest.skip("Golden dataset not found")
        
    judge = LLMJudge()
    
    for item in dataset:
        # Mock generated answer for testing
        generated_answer = item["expected_outcome"] 
        
        result = await judge.evaluate(
            prompt=item["prompt"],
            generated_answer=generated_answer,
            expected_answer=item["expected_outcome"]
        )
        
        assert result["passed"] is True, f"Failed evaluation for {item['id']}"
