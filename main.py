from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.responses import StreamingResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from database import SessionLocal, init_db, Job, EvalRun, PromptVersion, ExecutionLog
from context import SharedContext
from agents.orchestrator import OrchestratorAgent
from llm import LLMClient
from budget import BudgetManager
from logger import StructuredLogger
from eval.harness import EvalHarness
import uuid
import json
import asyncio
import os
from typing import Optional

app = FastAPI(title="Mega AI System")

# CORS for Vercel deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

# Serve Log UI at root
@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    ui_path = os.path.join(os.path.dirname(__file__), "log_ui", "index.html")
    with open(ui_path, "r") as f:
        return HTMLResponse(content=f.read())

@app.post("/submit")
async def submit_query(query: str, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    db = SessionLocal()
    job = Job(id=job_id, query=query, status="running")
    db.add(job)
    db.commit()
    db.close()
    
    # In a real system, this would go to a Redis queue
    # For this demo, we run it in background_tasks
    background_tasks.add_task(run_pipeline, job_id, query)
    
    return {"job_id": job_id, "message": "Job submitted"}

async def run_pipeline(job_id: str, query: str):
    llm = LLMClient()
    budget = BudgetManager()
    logger = StructuredLogger(job_id)
    context = SharedContext(job_id=job_id, original_query=query)
    
    orchestrator = OrchestratorAgent("orchestrator", llm, budget, logger)
    try:
        orchestrator.run(context)
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "completed"
        job.full_context = context.dict()
        db.commit()
        db.close()
    except Exception as e:
        db = SessionLocal()
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "failed"
        db.commit()
        db.close()

@app.get("/stream/{job_id}")
async def stream_logs(job_id: str):
    async def event_generator():
        last_id = 0
        while True:
            db = SessionLocal()
            logs = db.query(ExecutionLog).filter(
                ExecutionLog.job_id == job_id,
                ExecutionLog.id > last_id
            ).order_by(ExecutionLog.id.asc()).all()
            
            for log in logs:
                yield {
                    "event": log.event_type,
                    "data": json.dumps({
                        "agent": log.agent_id,
                        "content": log.content,
                        "timestamp": log.timestamp.isoformat()
                    })
                }
                last_id = log.id
            
            job = db.query(Job).filter(Job.id == job_id).first()
            db.close()
            
            if job and job.status in ["completed", "failed"]:
                yield {"event": "end", "data": "Job finished"}
                break
                
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())

@app.get("/trace/{job_id}")
async def get_trace(job_id: str):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    logs = db.query(ExecutionLog).filter(ExecutionLog.job_id == job_id).order_by(ExecutionLog.id.asc()).all()
    db.close()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return {
        "job": job,
        "logs": logs
    }

@app.get("/eval/latest")
async def get_latest_eval():
    db = SessionLocal()
    latest_runs = db.query(EvalRun).order_by(EvalRun.timestamp.desc()).limit(15).all()
    db.close()
    return latest_runs

@app.post("/prompt/approve/{prompt_id}")
async def approve_prompt(prompt_id: int):
    db = SessionLocal()
    prompt = db.query(PromptVersion).filter(PromptVersion.id == prompt_id).first()
    if not prompt:
        db.close()
        raise HTTPException(status_code=404, detail="Prompt version not found")
        
    # Deactivate others for same role
    db.query(PromptVersion).filter(PromptVersion.agent_role == prompt.agent_role).update({"is_active": False})
    prompt.is_active = True
    prompt.status = "approved"
    db.commit()
    db.close()
    return {"message": "Prompt approved and activated"}

@app.post("/eval/re-run")
async def trigger_re_eval(targeted_ids: Optional[list] = None):
    harness = EvalHarness()
    results = await harness.run_eval(targeted_ids)
    return results

# Health check for Vercel
@app.get("/health")
async def health_check():
    return {"status": "healthy", "system": "Mega AI Orchestration Engine"}
