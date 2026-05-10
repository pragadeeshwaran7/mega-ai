import asyncio
from database import SessionLocal, Job, init_db
from context import SharedContext
from agents.orchestrator import OrchestratorAgent
from llm import LLMClient
from budget import BudgetManager
from logger import StructuredLogger
import os

async def worker_loop():
    print("Worker started...")
    init_db()
    llm = LLMClient()
    budget = BudgetManager()

    while True:
        db = SessionLocal()
        # Find a job that is "submitted" but not yet "running" 
        # (This would need a 'submitted' status in Job model, but we'll adapt)
        job = db.query(Job).filter(Job.status == "submitted").first()
        
        if job:
            print(f"Processing job {job.id}...")
            job.status = "running"
            db.commit()
            
            logger = StructuredLogger(job.id)
            context = SharedContext(job_id=job.id, original_query=job.query)
            orchestrator = OrchestratorAgent("orchestrator", llm, budget, logger)
            
            try:
                orchestrator.run(context)
                job.status = "completed"
                job.full_context = context.dict()
            except Exception as e:
                print(f"Error: {e}")
                job.status = "failed"
            
            db.commit()
        
        db.close()
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(worker_loop())
