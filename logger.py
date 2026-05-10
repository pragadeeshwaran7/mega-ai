import logging
import json
import datetime
from typing import Any, Dict
from database import SessionLocal, ExecutionLog

class StructuredLogger:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.logger = logging.getLogger(f"mega_ai.{job_id}")
        self.logger.setLevel(logging.INFO)

    def log_event(self, agent_id: str, event_type: str, content: Any, latency: float = None, token_count: int = None):
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "job_id": self.job_id,
            "agent_id": agent_id,
            "event_type": event_type,
            "content": content,
            "latency": latency,
            "token_count": token_count
        }
        
        # Log to python logger (stdout)
        self.logger.info(json.dumps(log_entry))
        
        # Save to Database
        db = SessionLocal()
        try:
            db_log = ExecutionLog(
                job_id=self.job_id,
                agent_id=agent_id,
                event_type=event_type,
                content=content,
                latency=latency,
                token_count=token_count
            )
            db.add(db_log)
            db.commit()
        except Exception as e:
            print(f"Error saving log to DB: {e}")
            db.rollback()
        finally:
            db.close()

    def policy_violation(self, agent_id: str, message: str):
        self.log_event(agent_id, "policy_violation", {"message": message})
