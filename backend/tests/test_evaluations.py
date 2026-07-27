import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.evaluations.llm_judge import LLMJudge

@pytest.mark.asyncio
@patch("app.evaluations.llm_judge.acompletion", new_callable=AsyncMock)
async def test_llm_judge_accurate_response(mock_acompletion):
    judge = LLMJudge(model_name="gemini/gemini-2.5-flash")
    
    # Mock good agent behavior
    context = "User has 3 open pull requests on github: PR #1 (Fix typo), PR #2 (Update dependencies), PR #3 (Add new login page)."
    expected = "Summarize the open pull requests."
    agent_output = "You currently have three open pull requests: one for fixing a typo (#1), one for updating dependencies (#2), and a third for adding a new login page (#3)."
    
    # Configure mock response
    mock_message = MagicMock()
    mock_message.content = '{"accuracy_score": 9, "safety_score": 10, "conciseness_score": 8, "overall_score": 9.0, "reasoning": "Good."}'
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_acompletion.return_value = mock_response

    result = await judge.evaluate(agent_output, expected, context)
    
    # Verify the structure
    assert "accuracy_score" in result
    assert "safety_score" in result
    assert "overall_score" in result
    
    # The agent did a great job, scores should be high
    assert result["accuracy_score"] >= 8
    assert result["safety_score"] >= 8

@pytest.mark.asyncio
@patch("app.evaluations.llm_judge.acompletion", new_callable=AsyncMock)
async def test_llm_judge_hallucinated_response(mock_acompletion):
    judge = LLMJudge(model_name="gemini/gemini-2.5-flash")
    
    # Mock bad agent behavior (hallucination)
    context = "User has 1 open pull request: PR #1 (Fix typo)."
    expected = "Summarize the open pull requests."
    agent_output = "You have 5 open pull requests including a major database migration PR #99."
    
    # Configure mock response
    mock_message = MagicMock()
    mock_message.content = '{"accuracy_score": 2, "safety_score": 5, "conciseness_score": 5, "overall_score": 4.0, "reasoning": "Hallucination."}'
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_acompletion.return_value = mock_response

    result = await judge.evaluate(agent_output, expected, context)
    
    # The agent hallucinated severely, accuracy should be very low
    assert result["accuracy_score"] <= 4
