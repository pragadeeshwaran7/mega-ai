from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole
import json

class CritiqueAgent(BaseAgent):
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        history = context.get_full_history_text()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Review this execution history and provide a critique with confidence scores:\n{history}"}
        ]
        
        response = self.call_llm(messages)
        
        # Expecting JSON with scores and flags
        data = self.llm.parse_json(response)
        
        return AgentMessage(
            agent_role=self.role,
            content=response,
            confidence_score=data.get("overall_confidence", 0.5),
            thought_process="Critiquing every claim for adversarial robustness."
        )
