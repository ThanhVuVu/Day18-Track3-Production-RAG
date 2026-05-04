"""Production RAG Pipeline — Bài tập NHÓM: ghép M1+M2+M3+M4."""

import os
import sys
import time
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.m1_chunking import load_documents, chunk_hierarchical
from src.m2_search import HybridSearch
from src.m3_rerank import CrossEncoderReranker
from src.m4_eval import load_test_set, evaluate_ragas, failure_analysis, save_report
from src.m5_enrichment import enrich_chunks
from config import RERANK_TOP_K


def build_pipeline():
    """Build production RAG pipeline."""
    print("=" * 60)
    print("PRODUCTION RAG PIPELINE")
    print("=" * 60)

    # Step 1: Load & Chunk (M1)
    t0 = time.time()
    print("\n[1/3] Chunking documents...")
    docs = load_documents()
    all_chunks = []
    for doc in docs:
        parents, children = chunk_hierarchical(doc["text"], metadata=doc["metadata"])
        for child in children:
            all_chunks.append({
                "text": child.text, 
                "metadata": {**child.metadata, "parent_id": child.parent_id},
                "full_document_text": doc["text"] # Pass full text for Contextual Prepend
            })
    t1 = time.time()
    print(f"  {len(all_chunks)} chunks from {len(docs)} documents (Time: {t1-t0:.2f}s)")

    # Step 2: Enrichment (M5)
    print("\n[2/4] Enriching chunks (M5)...")
    enriched = enrich_chunks(all_chunks, methods=["contextual", "hyqa", "metadata"])
    if enriched:
        # Use enriched text for indexing
        all_chunks = [{"text": e.enriched_text, "metadata": e.auto_metadata} for e in enriched]
        print(f"  Enriched {len(enriched)} chunks")
    else:
        print("  [!] M5 not implemented — using raw chunks (fallback)")
        
    t2 = time.time()
    print(f"  Enrichment Time: {t2-t1:.2f}s")

    # Step 3: Index (M2)
    print("\n[3/4] Indexing (BM25 + Dense)...")
    search = HybridSearch()
    search.index(all_chunks)
    t3 = time.time()
    print(f"  Indexing Time: {t3-t2:.2f}s")

    # Step 4: Reranker (M3)
    print("\n[4/4] Loading reranker...")
    reranker = CrossEncoderReranker()
    t4 = time.time()
    print(f"  Reranker Load Time: {t4-t3:.2f}s")

    return search, reranker


def run_query(query: str, search: HybridSearch, reranker: CrossEncoderReranker) -> tuple[str, list[str]]:
    """Run single query through pipeline."""
    results = search.search(query)
    docs = [{"text": r.text, "score": r.score, "metadata": r.metadata} for r in results]
    reranked = reranker.rerank(query, docs, top_k=RERANK_TOP_K)
    contexts = [r.text for r in reranked] if reranked else [r.text for r in results[:3]]

    # LLM Generation for better scores (Faithfulness & Answer Relevancy)
    answer = "Không tìm thấy thông tin."
    if contexts:
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=os.environ.get("NVIDIA_API_KEY", "")
            )
            context_str = "\n\n".join(contexts)
            
            # System prompt chặt chẽ để đạt Faithfulness >= 0.85 (Bonus)
            sys_prompt = (
                "Bạn là trợ lý AI nội bộ. "
                "CHỈ ĐƯỢC trả lời dựa trên nội dung Context được cung cấp bên dưới. "
                "Tuyệt đối KHÔNG tự sáng tạo thông tin. "
                "Nếu Context không chứa đủ thông tin để trả lời, hãy nói 'Tôi không tìm thấy thông tin trong tài liệu'."
            )
            
            resp = client.chat.completions.create(
                model="meta/llama-3.1-70b-instruct", 
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Context:\n{context_str}\n\nCâu hỏi: {query}"},
                ],
                temperature=0.0 # Temperature 0 để LLM trả lời ổn định, trung thực nhất
            )
            answer = resp.choices[0].message.content
        except Exception as e:
            print(f"  [!] LLM error: {e} (Sử dụng fallback answer)")
            answer = contexts[0]
            
    return answer, contexts


def evaluate_pipeline(search: HybridSearch, reranker: CrossEncoderReranker):
    """Run evaluation on test set."""
    print("\n[Eval] Running queries...")
    test_set = load_test_set()
    questions, answers, all_contexts, ground_truths = [], [], [], []

    t_q_start = time.time()
    for i, item in enumerate(test_set):
        answer, contexts = run_query(item["question"], search, reranker)
        questions.append(item["question"])
        answers.append(answer)
        all_contexts.append(contexts)
        ground_truths.append(item["ground_truth"])
        print(f"  [{i+1}/{len(test_set)}] {item['question'][:50]}...")
    query_time = time.time() - t_q_start

    print("\n[Eval] Running RAGAS...")
    t_e_start = time.time()
    results = evaluate_ragas(questions, answers, all_contexts, ground_truths)
    eval_time = time.time() - t_e_start

    print("\n" + "=" * 60)
    print("PRODUCTION RAG SCORES")
    print("=" * 60)
    for m in ["faithfulness", "answer_relevancy", "context_precision", "context_recall"]:
        s = results.get(m, 0)
        print(f"  {'✓' if s >= 0.75 else '✗'} {m}: {s:.4f}")

    failures = failure_analysis(results.get("per_question", []))
    save_report(results, failures)
    
    # Latency report
    print("\n" + "=" * 60)
    print("LATENCY BREAKDOWN REPORT")
    print("=" * 60)
    print(f"  - Average latency per query: {query_time / max(1, len(test_set)):.2f}s")
    print(f"  - Total queries time: {query_time:.2f}s")
    print(f"  - Total RAGAS eval time: {eval_time:.2f}s")
    
    return results


if __name__ == "__main__":
    start = time.time()
    search, reranker = build_pipeline()
    evaluate_pipeline(search, reranker)
    print(f"\nTotal: {time.time() - start:.1f}s")
