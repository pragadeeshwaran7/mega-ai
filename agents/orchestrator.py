from agents.base import BaseAgent
from agents.decomposition import DecompositionAgent
from agents.rag import RAGAgent
from agents.critique import CritiqueAgent
from agents.synthesis import SynthesisAgent
from context import SharedContext, AgentMessage, AgentRole
from budget import CompressionManager
from agents.compression import CompressionAgent
import json

class OrchestratorAgent(BaseAgent):
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        # Check if budget is exceeded before starting
        total_tokens = sum(context.token_usage.values())
        if total_tokens > self.budget_manager.limit:
            self.logger.policy_violation(self.role.value, f"Budget exceeded: {total_tokens}")
            # Trigger compression
            comp_agent = CompressionAgent(AgentRole.COMPRESSION, self.llm, self.budget_manager, self.logger)
            context.history = CompressionManager.compress_history(context.history, comp_agent.run)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Current History:\n{context.get_full_history_text()}\nOriginal Query: {context.original_query}"}
        ]
        
        response = self.call_llm(messages)
        routing_decision = self.llm.parse_json(response)
        
        next_agent_role = routing_decision.get("next_agent")
        reasoning = routing_decision.get("reasoning")
        
        if not next_agent_role or next_agent_role == "FINISH":
            return AgentMessage(agent_role=self.role, content="FINISH", thought_process=reasoning)
        
        # Instantiate and run next agent
        agent_map = {
            AgentRole.DECOMPOSITION: DecompositionAgent,
            AgentRole.RAG: RAGAgent,
            AgentRole.CRITIQUE: CritiqueAgent,
            AgentRole.SYNTHESIS: SynthesisAgent
        }
        
        agent_cls = agent_map.get(AgentRole(next_agent_role))
        if agent_cls:
            agent = agent_cls(AgentRole(next_agent_role), self.llm, self.budget_manager, self.logger)
            msg = agent.run(context)
            context.add_message(msg)
            
            # Recursive call to orchestrate next step
            return self.run(context)
        
        return AgentMessage(agent_role=self.role, content="ERROR: Invalid agent routed", thought_process=reasoning)
