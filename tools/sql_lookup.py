from tools.base import Tool
from typing import Any, Dict
from database import engine
import pandas as pd

class SQLLookupTool(Tool):
    @property
    def name(self) -> str:
        return "sql_lookup"

    @property
    def description(self) -> str:
        return "Query the local database using SQL. Input: sql (str)."

    def execute(self, sql: str = None, **kwargs) -> Dict[str, Any]:
        if not sql:
            return {"output": "No SQL provided", "status": "error"}

        try:
            # Prevent destructive queries
            forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
            if any(word in sql.upper() for word in forbidden):
                return {"output": "Only SELECT queries are allowed", "status": "error"}

            df = pd.read_sql(sql, engine)
            results = df.to_dict(orient="records")
            
            if not results:
                return {"output": [], "status": "empty"}

            return {
                "output": results,
                "status": "success"
            }
        except Exception as e:
            return {
                "output": str(e),
                "status": "error"
            }
        finally:
            engine.dispose()
