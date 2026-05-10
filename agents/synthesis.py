from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole
import json

class SynthesisAgent(BaseAgent):
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        history = context.get_full_history_text()
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Merge all findings and resolve contradictions from the history:\n{history}"}
        ]
        
        response = self.call_llm(messages)
        
        # Build provenance map (simulated here)
        provenance = {}
        for i, sentence in enumerate(response.split(". ")):
            provenance[f"sentence_{i}"] = {
                "source_agent": "rag" if "Source" in sentence else "synthesis",
                "text": sentence
            }
        
        context.provenance_map = provenance
        
        return AgentMessage(
            agent_role=self.role,
            content=response
        )
