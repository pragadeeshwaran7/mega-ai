from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole
from typing import List

class CompressionAgent(BaseAgent):
    def run(self, history: List[AgentMessage], **kwargs) -> str:
        history_text = "\n".join([f"{m.agent_role.value}: {m.content}" for m in history])
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Compress the following history:\n{history_text}"}
        ]
        
        return self.call_llm(messages)
