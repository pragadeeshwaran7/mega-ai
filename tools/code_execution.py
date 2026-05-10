from tools.base import Tool
from typing import Any, Dict
import sys
import io
import traceback

class CodeExecutionTool(Tool):
    @property
    def name(self) -> str:
        return "code_execution"

    @property
    def description(self) -> str:
        return "Execute Python code snippets. Input: code (str)."

    def execute(self, code: str = None, **kwargs) -> Dict[str, Any]:
        if not code:
            return {"output": "No code provided", "status": "error"}

        # Redirect stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = io.StringIO()
        redirected_error = sys.stderr = io.StringIO()

        exit_code = 0
        try:
            # Dangerous in production, but requested for this sandbox demo
            exec(code, {"__builtins__": __builtins__}, {})
        except Exception:
            exit_code = 1
            print(traceback.format_exc(), file=sys.stderr)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()

        return {
            "output": {
                "stdout": stdout,
                "stderr": stderr,
                "exit_code": exit_code
            },
            "status": "success" if exit_code == 0 else "error"
        }
