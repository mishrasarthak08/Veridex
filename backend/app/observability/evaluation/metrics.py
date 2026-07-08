class EvaluationMetrics:
    @staticmethod
    def calculate_correctness(expected: str, actual: str) -> float:
        # Mock calculation: if expected keywords are in actual
        # Real implementation would use embedding similarity or LLM judge
        return 0.85

    @staticmethod
    def calculate_hallucination_score(ground_truth: str, generated: str) -> float:
        # Lower is better. Mock logic.
        return 0.1
