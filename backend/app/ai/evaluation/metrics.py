import json
from app.ai.router import router

class EvaluationFramework:
    """
    Framework to evaluate the quality of AI responses using an LLM-as-a-Judge.
    """
    def __init__(self):
        pass

    async def evaluate_goal_completion(self, goal: str, final_output: str) -> float:
        """
        Uses the LLM router to score whether the final_output met the goal.
        Returns a float between 0.0 and 1.0.
        """
        prompt = f"Goal: {goal}\n\nOutput: {final_output}\n\nDid the output successfully achieve the goal? Reply with a JSON object containing a 'score' field (0.0 for failure, 1.0 for success) and a 'reason' string."
        
        try:
            response = await router.generate(
                messages=[{"role": "user", "content": prompt}],
                task_type="default"
            )
            content = response.get("content", "{}")
            # Minimal parsing logic for the JSON block
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            
            data = json.loads(content)
            return float(data.get("score", 0.0))
        except Exception as e:
            print(f"[Evaluation] Error evaluating goal completion: {e}")
            return 0.0

evaluator = EvaluationFramework()
