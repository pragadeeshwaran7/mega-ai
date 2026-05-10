from eval.test_cases import TEST_CASES
from eval.scoring import Scorer
from context import SharedContext
from agents.orchestrator import OrchestratorAgent
from llm import LLMClient
from budget import BudgetManager
from logger import StructuredLogger
from database import SessionLocal, EvalRun, Job
import uuid
import datetime

class EvalHarness:
    def __init__(self):
        self.llm = LLMClient()
        self.budget_manager = BudgetManager()
        self.scorer = Scorer()

    async def run_eval(self, targeted_ids: list = None):
        db = SessionLocal()
        results = []
        
        test_cases = TEST_CASES
        if targeted_ids:
            test_cases = [t for t in TEST_CASES if t["id"] in targeted_ids]

        for tc in test_cases:
            job_id = str(uuid.uuid4())
            logger = StructuredLogger(job_id)
            context = SharedContext(job_id=job_id, original_query=tc["query"])
            
            # Save Job
            db_job = Job(id=job_id, query=tc["query"], status="running")
            db.add(db_job)
            db.commit()

            try:
                orchestrator = OrchestratorAgent("orchestrator", self.llm, self.budget_manager, logger)
                orchestrator.run(context)
                
                # Score
                eval_result = self.scorer.score_run(context, tc["expected"])
                
                # Save Eval Run
                db_eval = EvalRun(
                    test_case_id=tc["id"],
                    category=tc["category"],
                    scores=eval_result["dimensions"],
                    total_score=eval_result["total"],
                    job_id=job_id
                )
                db.add(db_eval)
                
                db_job.status = "completed"
                db_job.completed_at = datetime.datetime.utcnow()
                db_job.full_context = context.dict()
                db.commit()
                
                results.append(eval_result)
            except Exception as e:
                print(f"Error in eval for {tc['id']}: {e}")
                db_job.status = "failed"
                db.commit()
        
        db.close()
        return results
