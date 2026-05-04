"""Module 4: RAGAS Evaluation — 4 metrics + failure analysis."""

import os
import sys
import json
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TEST_SET_PATH


@dataclass
class EvalResult:
    question: str
    answer: str
    contexts: list[str]
    ground_truth: str
    faithfulness: float
    answer_relevancy: float
    context_precision: float
    context_recall: float


def load_test_set(path: str = TEST_SET_PATH) -> list[dict]:
    """Load test set from JSON. (Đã implement sẵn)"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def evaluate_ragas(questions: list[str], answers: list[str],
                   contexts: list[list[str]], ground_truths: list[str]) -> dict:
    # Implement RAGAS evaluation with try-except for missing API keys
    try:
        from ragas.metrics import faithfulness, answer_relevancy, context_precision, context_recall
        from datasets import Dataset
        from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
        
        dataset = Dataset.from_dict({
            "question": questions, "answer": answers,
            "contexts": contexts, "ground_truth": ground_truths,
        })
        
        nvidia_llm = ChatNVIDIA(
            model="meta/llama-3.1-70b-instruct",
            nvidia_api_key=os.environ.get("NVIDIA_API_KEY", ""),
            temperature=0,
            timeout=300
        )
        
        nvidia_embeddings = NVIDIAEmbeddings(
            model="nvidia/nv-embedqa-e5-v5",
            nvidia_api_key=os.environ.get("NVIDIA_API_KEY", "")
        )
        
        from ragas import evaluate, RunConfig
        
        # Configure evaluation to avoid rate limits and timeouts
        run_config = RunConfig(max_workers=1, timeout=300)
        
        result = evaluate(
            dataset, 
            metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
            llm=nvidia_llm,
            embeddings=nvidia_embeddings,
            run_config=run_config
        )
        df = result.to_pandas()
        
        per_question = [
            EvalResult(
                question=row.get("user_input", row.get("question", "")),
                answer=row.get("response", row.get("answer", "")),
                contexts=row.get("retrieved_contexts", row.get("contexts", [])),
                ground_truth=row.get("reference", row.get("ground_truth", "")),
                faithfulness=row.get("faithfulness", 0.0),
                answer_relevancy=row.get("answer_relevancy", 0.0),
                context_precision=row.get("context_precision", 0.0),
                context_recall=row.get("context_recall", 0.0)
            ) for _, row in df.iterrows()
        ]
        
        def safe_get(res, key):
            import math
            try:
                val = res.get(key, 0.0) if hasattr(res, "get") else res[key]
                if hasattr(val, "item") and not hasattr(val, "__iter__"): 
                    val = val.item()
                if isinstance(val, (list, tuple)) or (hasattr(val, "__iter__") and not isinstance(val, str)):
                    val = sum(val) / len(val) if len(val) > 0 else 0.0
                
                f_val = float(val)
                return f_val if not math.isnan(f_val) else 0.0
            except Exception:
                return 0.0

        return {
            "faithfulness": safe_get(result, "faithfulness"), 
            "answer_relevancy": safe_get(result, "answer_relevancy"),
            "context_precision": safe_get(result, "context_precision"), 
            "context_recall": safe_get(result, "context_recall"), 
            "per_question": per_question
        }
    except Exception as e:
        print(f"  [!] RAGAS eval error: {e} (Chưa cấu hình NVIDIA_API_KEY?)")
        # Fallback values
        return {"faithfulness": 0.0, "answer_relevancy": 0.0,
                "context_precision": 0.0, "context_recall": 0.0, "per_question": []}


def failure_analysis(eval_results: list[EvalResult], bottom_n: int = 10) -> list[dict]:
    if not eval_results:
        return []
        
    failures = []
    # Calculate avg score and sort
    for res in eval_results:
        avg = (res.faithfulness + res.answer_relevancy + res.context_precision + res.context_recall) / 4.0
        failures.append({"res": res, "avg": avg})
        
    failures.sort(key=lambda x: x["avg"])
    bottom = failures[:bottom_n]
    
    analysis = []
    for item in bottom:
        res = item["res"]
        scores = {
            "faithfulness": res.faithfulness,
            "answer_relevancy": res.answer_relevancy,
            "context_precision": res.context_precision,
            "context_recall": res.context_recall
        }
        # Find worst metric
        worst_metric = min(scores, key=scores.get)
        worst_score = scores[worst_metric]
        
        # Diagnose
        diagnosis, fix = "Unknown", "Check pipeline"
        if worst_metric == "faithfulness" and worst_score < 0.85:
            diagnosis = "LLM hallucinating"
            fix = "Tighten prompt, lower temperature"
        elif worst_metric == "context_recall" and worst_score < 0.75:
            diagnosis = "Missing relevant chunks"
            fix = "Improve chunking or add BM25"
        elif worst_metric == "context_precision" and worst_score < 0.75:
            diagnosis = "Too many irrelevant chunks"
            fix = "Add reranking or metadata filter"
        elif worst_metric == "answer_relevancy" and worst_score < 0.80:
            diagnosis = "Answer doesn't match question"
            fix = "Improve prompt template"
            
        analysis.append({
            "question": res.question,
            "worst_metric": worst_metric,
            "score": worst_score,
            "diagnosis": diagnosis,
            "suggested_fix": fix
        })
        
    return analysis


def save_report(results: dict, failures: list[dict], path: str = "ragas_report.json"):
    """Save evaluation report to JSON. (Đã implement sẵn)"""
    # Ensure report is saved in reports/ folder
    if not os.path.dirname(path):
        path = os.path.join("reports", path)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
        
    report = {
        "aggregate": {k: v for k, v in results.items() if k != "per_question"},
        "num_questions": len(results.get("per_question", [])),
        "failures": failures,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Report saved to {path}")


if __name__ == "__main__":
    test_set = load_test_set()
    print(f"Loaded {len(test_set)} test questions")
    print("Run pipeline.py first to generate answers, then call evaluate_ragas().")
