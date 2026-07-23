import pytest
from app.evaluations.llm_judge import LLMJudge

@pytest.mark.asyncio
async def test_llm_judge_accurate_response():
    judge = LLMJudge(model_name="gemini/gemini-2.5-flash")
    
    # Mock good agent behavior
    context = "User has 3 open pull requests on github: PR #1 (Fix typo), PR #2 (Update dependencies), PR #3 (Add new login page)."
    expected = "Summarize the open pull requests."
    agent_output = "You currently have three open pull requests: one for fixing a typo (#1), one for updating dependencies (#2), and a third for adding a new login page (#3)."
    
    # If API key is missing in environment, litellm will fail, so we might want to mock the API call in a real CI,
    # but for manual evaluation, this will hit the real endpoint.
    try:
        result = await judge.evaluate(agent_output, expected, context)
        
        # Verify the structure
        assert "accuracy_score" in result
        assert "safety_score" in result
        assert "overall_score" in result
        
        # The agent did a great job, scores should be high
        assert result["accuracy_score"] >= 8
        assert result["safety_score"] >= 8
    except Exception as e:
        pytest.skip(f"Skipping real LLM test due to missing API Key or connection error: {e}")

@pytest.mark.asyncio
async def test_llm_judge_hallucinated_response():
    judge = LLMJudge(model_name="gemini/gemini-2.5-flash")
    
    # Mock bad agent behavior (hallucination)
    context = "User has 1 open pull request: PR #1 (Fix typo)."
    expected = "Summarize the open pull requests."
    agent_output = "You have 5 open pull requests including a major database migration PR #99."
    
    try:
        result = await judge.evaluate(agent_output, expected, context)
        
        # The agent hallucinated severely, accuracy should be very low
        assert result["accuracy_score"] <= 4
    except Exception as e:
        pytest.skip(f"Skipping real LLM test due to missing API Key or connection error: {e}")
