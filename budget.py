import tiktoken
from typing import List
from context import SharedContext, AgentMessage, AgentRole

class BudgetManager:
    def __init__(self, model_name: str = "gpt-4", limit: int = 4000):
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        self.limit = limit

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def check_budget(self, context: SharedContext, agent_role: str, new_content: str) -> bool:
        current_usage = context.token_usage.get(agent_role, 0)
        new_tokens = self.count_tokens(new_content)
        total = current_usage + new_tokens
        
        if total > self.limit:
            return False
        return True

    def get_remaining_budget(self, context: SharedContext, agent_role: str) -> int:
        current_usage = context.token_usage.get(agent_role, 0)
        return max(0, self.limit - current_usage)

class CompressionManager:
    @staticmethod
    def compress_history(history: List[AgentMessage], compression_agent_callback) -> List[AgentMessage]:
        """
        Compresses the history by summarizing older conversational parts 
        while preserving structured data (tool calls, citations).
        """
        # Logic: Keep the last 2 messages as is. Summarize everything before.
        if len(history) <= 3:
            return history
            
        to_summarize = history[:-2]
        preserved = history[-2:]
        
        summary_text = compression_agent_callback(to_summarize)
        
        summary_message = AgentMessage(
            agent_role=AgentRole.COMPRESSION,
            content=f"SUMMARY OF PREVIOUS CONTEXT: {summary_text}",
            thought_process="Lossless compression for structured data, lossy for filler."
        )
        
        return [summary_message] + preserved
