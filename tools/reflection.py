from tools.base import Tool
from typing import Any, Dict
from context import SharedContext

class ReflectionTool(Tool):
    @property
    def name(self) -> str:
        return "self_reflection"

    @property
    def description(self) -> str:
        return "Re-read your previous outputs and identify contradictions or gaps. Input: None."

    def execute(self, context: SharedContext = None, **kwargs) -> Dict[str, Any]:
        if not context:
            return {"output": "Context not provided", "status": "error"}
        
        history = context.get_full_history_text()
        
        # This tool's "output" is just the history, 
        # but it triggers the agent to "reflect" on it.
        return {
            "output": f"Current history summary:\n{history}\n\nPlease identify any contradictions or gaps in the logic provided so far.",
            "status": "success"
        }
