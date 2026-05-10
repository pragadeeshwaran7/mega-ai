from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Use /tmp for SQLite on Vercel (read-only filesystem except /tmp)
# Use DATABASE_URL env var for PostgreSQL in Docker
_default_db = "sqlite:////tmp/mega_ai.db" if os.path.exists("/tmp") else "sqlite:///./mega_ai.db"
DATABASE_URL = os.getenv("DATABASE_URL", _default_db)

# Handle SQLite connect args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    query = Column(Text)
    status = Column(String) # "running", "completed", "failed"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    full_context = Column(JSON) # Serialized SharedContext

class ExecutionLog(Base):
    __tablename__ = "execution_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey("jobs.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    agent_id = Column(String)
    event_type = Column(String) # "thought", "message", "tool_call", "error"
    content = Column(JSON)
    latency = Column(Float, nullable=True)
    token_count = Column(Integer, nullable=True)

class EvalRun(Base):
    __tablename__ = "eval_runs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    test_case_id = Column(String)
    category = Column(String) # "straightforward", "ambiguous", "adversarial"
    scores = Column(JSON) # {dimension: {score: float, justification: str}}
    total_score = Column(Float)
    job_id = Column(String, ForeignKey("jobs.id"))

class PromptVersion(Base):
    __tablename__ = "prompt_versions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_role = Column(String)
    content = Column(Text)
    version = Column(Integer)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    proposed_by_eval_run_id = Column(Integer, nullable=True)
    justification = Column(Text, nullable=True)
    status = Column(String, default="pending") # "pending", "approved", "rejected"

# Database helper
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
