from abc import ABC, abstractmethod
from typing import Any, Dict
import time

class Tool(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Must return a dict with:
        - output: Any
        - status: "success" | "error" | "timeout" | "empty"
        - latency: float
        """
        pass

    def run(self, **kwargs) -> Dict[str, Any]:
        start_time = time.time()
        try:
            result = self.execute(**kwargs)
            result["latency"] = time.time() - start_time
            return result
        except Exception as e:
            return {
                "output": str(e),
                "status": "error",
                "latency": time.time() - start_time
            }
