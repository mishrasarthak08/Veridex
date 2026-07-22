import json
import litellm
from typing import List, Dict, Any

class GraphExtractor:
    def __init__(self, model_name: str = "gemini/gemini-2.5-flash"):
        self.model_name = model_name

    async def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Uses an LLM to extract entities and relationships from unstructured text.
        Returns a list of dicts like:
        [
            {"source": "EntityA", "target": "EntityB", "type": "RELATED_TO", "description": "context..."}
        ]
        """
        prompt = f"""
        Extract key entities and their relationships from the following text.
        Return the result as a JSON array of objects, where each object has:
        - "source": name of the first entity
        - "target": name of the second entity
        - "type": the relationship type (e.g. USES, BELONGS_TO, DEPENDS_ON) (UPPERCASE, NO SPACES)
        - "description": a brief description of how they relate

        Text:
        {text}
        """

        try:
            response = await litellm.acompletion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            content = response.choices[0].message.content
            # litellm json_object response is usually wrapped in a root object depending on the provider,
            # or could just be the array. We try to parse it.
            data = json.loads(content)
            
            if isinstance(data, dict):
                # Look for the first array in the dict values
                for v in data.values():
                    if isinstance(v, list):
                        return v
                return []
            elif isinstance(data, list):
                return data
            return []
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return []
