import json
from typing import Dict, Any, List
from app.ai.router import query_llm
from pydantic import BaseModel

class EvaluationResult(BaseModel):
    id: str
    goal: str
    score: int
    feedback: str
    status: str

class LLMJudge:
    def __init__(self, prompt_version: str = "v1"):
        self.prompt_version = prompt_version
        
    def _get_prompt(self, goal: str, result: str) -> str:
        if self.prompt_version == "v1":
            return f"""
            You are an expert evaluator. Evaluate the following execution.
            Goal: {goal}
            Result: {result}
            
            Score the result from 0 to 10 on how well it answered the goal.
            Return a JSON object with 'score' (int) and 'feedback' (string).
            """
        return "Invalid prompt version."

    async def evaluate_execution(self, exec_id: str, goal: str, result: str) -> EvaluationResult:
        prompt = self.get_prompt(goal, result)
        
        try:
            # We use litellm through query_llm, assuming it returns text
            llm_response = await query_llm(
                prompt=prompt,
                provider="openai", # or mocked
                model="gpt-4"      # or mock model
            )
            
            # parse JSON from LLM response
            # for robustness, we do a simple search or assume strict json format
            start_idx = llm_response.find('{')
            end_idx = llm_response.rfind('}') + 1
            if start_idx != -1 and end_idx != -1:
                parsed = json.loads(llm_response[start_idx:end_idx])
                score = parsed.get("score", 0)
                feedback = parsed.get("feedback", "No feedback provided")
            else:
                score = 0
                feedback = "Failed to parse LLM JSON"
                
            return EvaluationResult(
                id=exec_id,
                goal=goal,
                score=score,
                feedback=feedback,
                status="completed"
            )
            
        except Exception as e:
            return EvaluationResult(
                id=exec_id,
                goal=goal,
                score=0,
                feedback=str(e),
                status="failed"
            )

    def get_prompt(self, goal: str, result: str) -> str:
        return self._get_prompt(goal, result)
