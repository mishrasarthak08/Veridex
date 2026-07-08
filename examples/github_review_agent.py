"""
Example: GitHub Code Review Agent
Demonstrates how to use the extensibility framework to build a custom tool
and pass it to an agent.
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sdk", "python")))
from veridex.ext.base import BaseTool

class GitHubReviewTool(BaseTool):
    @property
    def name(self) -> str:
        return "github_reviewer"
        
    def execute(self, repo_url: str, pr_number: int) -> dict:
        print(f"Fetching PR {pr_number} from {repo_url}...")
        # Mock logic
        return {
            "status": "success",
            "findings": [
                {"file": "main.py", "issue": "Missing docstrings on Line 42"},
                {"file": "auth.py", "issue": "Hardcoded secret on Line 15"}
            ]
        }

if __name__ == "__main__":
    tool = GitHubReviewTool()
    print("Testing custom GitHub Tool:")
    print(tool.execute("https://github.com/example/repo", 42))
