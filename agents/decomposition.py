from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole, SubTask
from typing import List
import json

class DecompositionAgent(BaseAgent):
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Query: {context.original_query}"}
        ]
        
        response = self.call_llm(messages)
        data = self.llm.parse_json(response)
        
        subtasks = []
        if isinstance(data, list):
            for t in data:
                subtasks.append(SubTask(**t))
        elif "tasks" in data:
            for t in data["tasks"]:
                subtasks.append(SubTask(**t))
        
        context.subtasks = subtasks
        
        return AgentMessage(
            agent_role=self.role,
            content=f"Decomposed query into {len(subtasks)} sub-tasks.",
            thought_process=response
        )
