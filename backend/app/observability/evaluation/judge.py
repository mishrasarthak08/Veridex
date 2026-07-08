from .metrics import EvaluationMetrics

class LLMJudge:
    def __init__(self, model_name: str = "gpt-4o"):
        self.model_name = model_name

    async def evaluate(self, prompt: str, generated_answer: str, expected_answer: str) -> dict:
        """
        Uses an LLM to evaluate the answer based on correctness, 
        factual grounding, and clarity.
        """
        # Simulated LLM Judge
        correctness = EvaluationMetrics.calculate_correctness(expected_answer, generated_answer)
        hallucination = EvaluationMetrics.calculate_hallucination_score(expected_answer, generated_answer)
        
        return {
            "judge_model": self.model_name,
            "correctness_score": correctness,
            "hallucination_score": hallucination,
            "passed": correctness >= 0.8 and hallucination < 0.2
        }
