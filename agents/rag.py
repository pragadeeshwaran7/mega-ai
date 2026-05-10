from agents.base import BaseAgent
from context import SharedContext, AgentMessage, AgentRole
from tools.web_search import WebSearchTool

class RAGAgent(BaseAgent):
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        search_tool = WebSearchTool()
        
        # Hop 1
        query1 = context.original_query
        res1 = self.handle_tool_call(search_tool, context, query=query1)
        
        # Hop 2: Generate a follow-up query based on first result
        messages = [
            {"role": "system", "content": "Generate a follow-up search query to dive deeper into the specific facts found."},
            {"role": "user", "content": f"Original Query: {query1}\nFirst Results: {res1.output_data}"}
        ]
        query2 = self.call_llm(messages)
        res2 = self.handle_tool_call(search_tool, context, query=query2)
        
        # Synthesis
        final_messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Query: {query1}\nSource 1: {res1.output_data}\nSource 2: {res2.output_data}"}
        ]
        final_answer = self.call_llm(final_messages)
        
        return AgentMessage(
            agent_role=self.role,
            content=final_answer,
            tool_calls=[res1, res2]
        )
