from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
import uuid
import datetime

class AgentRole(str, Enum):
    ORCHESTRATOR = "orchestrator"
    DECOMPOSITION = "decomposition"
    RAG = "rag"
    CRITIQUE = "critique"
    SYNTHESIS = "synthesis"
    COMPRESSION = "compression"
    META = "meta"

class ToolResult(BaseModel):
    tool_name: str
    input_data: Any
    output_data: Any
    status: str # "success", "timeout", "error", "empty"
    latency: float
    accepted_by_agent: bool = True
    retry_count: int = 0

class AgentMessage(BaseModel):
    agent_role: AgentRole
    content: str
    thought_process: Optional[str] = None
    confidence_score: Optional[float] = None
    tool_calls: List[ToolResult] = []
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class SubTask(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    task_type: str
    dependencies: List[str] = []
    status: str = "pending" # "pending", "in_progress", "completed", "failed"
    assigned_agent: Optional[AgentRole] = None
    output: Optional[str] = None

class SharedContext(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    original_query: str
    history: List[AgentMessage] = []
    subtasks: List[SubTask] = []
    token_usage: Dict[str, int] = {} # agent_role -> total_tokens
    budget_limit: int = 4000
    provenance_map: Dict[str, Any] = {} # maps sentences to source agent/chunks
    metadata: Dict[str, Any] = {}

    def add_message(self, message: AgentMessage):
        self.history.append(message)
    
    def get_full_history_text(self) -> str:
        return "\n".join([f"{m.agent_role.value}: {m.content}" for m in self.history])

    def update_budget(self, agent_role: str, tokens: int):
        if agent_role not in self.token_usage:
            self.token_usage[agent_role] = 0
        self.token_usage[agent_role] += tokens
