from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from context import SharedContext, AgentMessage, AgentRole, ToolResult
from llm import LLMClient
from prompts import get_prompt
from budget import BudgetManager
from logger import StructuredLogger
import time

class BaseAgent(ABC):
    def __init__(self, role: AgentRole, llm: LLMClient, budget_manager: BudgetManager, logger: StructuredLogger):
        self.role = role
        self.llm = llm
        self.budget_manager = budget_manager
        self.logger = logger
        self.system_prompt = get_prompt(role)

    @abstractmethod
    def run(self, context: SharedContext, **kwargs) -> AgentMessage:
        pass

    def call_llm(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        start_time = time.time()
        response = self.llm.completion(messages, stream=stream)
        latency = time.time() - start_time
        tokens = self.budget_manager.count_tokens(str(response))
        
        self.logger.log_event(self.role.value, "llm_call", {"latency": latency, "tokens": tokens})
        return response

    def handle_tool_call(self, tool, context: SharedContext, **tool_args) -> ToolResult:
        start_time = time.time()
        result = tool.run(**tool_args, context=context)
        latency = time.time() - start_time
        
        tool_result = ToolResult(
            tool_name=tool.name,
            input_data=tool_args,
            output_data=result["output"],
            status=result["status"],
            latency=latency
        )
        
        self.logger.log_event(self.role.value, "tool_call", tool_result.dict())
        return tool_result
