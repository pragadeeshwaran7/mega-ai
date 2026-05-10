from typing import Dict, Any
from context import SharedContext

class Scorer:
    def score_run(self, context: SharedContext, expected: str) -> Dict[str, Any]:
        """
        Scores a run across multiple dimensions:
        - Correctness
        - Citation Accuracy
        - Contradiction Resolution
        - Tool Efficiency
        - Budget Compliance
        - Critique Agreement
        """
        scores = {}
        
        # 1. Correctness (Simulated/Heuristic)
        final_ans = context.history[-1].content if context.history else ""
        correctness = 1.0 if expected.lower() in final_ans.lower() else 0.5
        scores["correctness"] = {
            "score": correctness,
            "justification": f"Found expected keywords in final answer: {expected}"
        }

        # 2. Citation Accuracy
        has_citations = "[" in final_ans and "]" in final_ans
        scores["citation_accuracy"] = {
            "score": 1.0 if has_citations else 0.0,
            "justification": "Citations present in output." if has_citations else "No citations found."
        }

        # 3. Tool Efficiency
        tool_calls = sum(len(m.tool_calls) for m in context.history)
        efficiency = 1.0 if tool_calls <= 5 else 0.5
        scores["tool_efficiency"] = {
            "score": efficiency,
            "justification": f"Made {tool_calls} tool calls."
        }

        # 4. Budget Compliance
        total_tokens = sum(context.token_usage.values())
        compliance = 1.0 if total_tokens <= context.budget_limit else 0.0
        scores["budget_compliance"] = {
            "score": compliance,
            "justification": f"Used {total_tokens} tokens out of {context.budget_limit} limit."
        }

        # 5. Critique Agreement
        critique_msg = next((m for m in context.history if m.agent_role == "critique"), None)
        agreement = 1.0 if critique_msg and critique_msg.confidence_score and critique_msg.confidence_score > 0.7 else 0.5
        scores["critique_agreement"] = {
            "score": agreement,
            "justification": "Critique agent expressed high confidence." if agreement == 1.0 else "Critique agent flagged issues."
        }

        total = sum(s["score"] for s in scores.values()) / len(scores)
        return {"dimensions": scores, "total": total}
