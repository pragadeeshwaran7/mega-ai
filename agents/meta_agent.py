from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole
from typing import List, Dict

class MetaAgent(BaseAgent):
    def run(self, failure_cases: List[Dict], worst_prompt: str, dimension: str) -> Dict:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Worst performing prompt for {dimension}:\n{worst_prompt}\n\nFailure examples:\n{json.dumps(failure_cases)}"}
        ]
        
        response = self.call_llm(messages)
        data = self.llm.parse_json(response)
        
        return {
            "proposed_content": data.get("new_prompt"),
            "justification": data.get("justification"),
            "diff": data.get("diff")
        }
import json
