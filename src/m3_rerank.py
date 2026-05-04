"""Module 3: Reranking — Cross-encoder top-20 → top-3 + latency benchmark."""

import os
import sys
import time
import logging
from dataclasses import dataclass
from config import RERANK_TOP_K  # noqa: E402

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
@dataclass
class RerankResult:
    text: str
    original_score: float
    rerank_score: float
    metadata: dict
    rank: int


class CrossEncoderReranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        self._model = None

    def _load_model(self):
        if self._model is None:
            logger.info(f"Đang tải mô hình CrossEncoder ({self.model_name}). Việc này có thể mất thời gian trong lần chạy đầu tiên do tải file...")
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.model_name)
            logger.info("Tải mô hình CrossEncoder thành công!")
        return self._model

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        """Rerank documents: top-20 → top-k."""
        if not documents:
            return []
            
        model = self._load_model()
        pairs = [(query, doc["text"]) for doc in documents]
        
        try:
            scores = model.predict(pairs)
        except AttributeError:
            # For FlagReranker compatibility if changed later
            scores = model.compute_score(pairs)
            
        scored_docs = [(score, doc) for score, doc in zip(scores, documents)]
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        results = []
        for i, (score, doc) in enumerate(scored_docs[:top_k]):
            results.append(RerankResult(
                text=doc["text"],
                original_score=doc.get("score", 0.0),
                rerank_score=float(score),
                metadata=doc.get("metadata", {}),
                rank=i+1
            ))
            
        return results


class FlashrankReranker:
    """Lightweight alternative (<5ms). Optional."""
    def __init__(self):
        self._model = None

    def rerank(self, query: str, documents: list[dict], top_k: int = RERANK_TOP_K) -> list[RerankResult]:
        from flashrank import Ranker, RerankRequest
        if self._model is None:
            logger.info("Đang tải mô hình FlashRank. Lần đầu tiên sẽ mất thời gian download...")
            self._model = Ranker()
            logger.info("Tải mô hình FlashRank thành công!")
            
        passages = [{"id": i, "text": d["text"], "meta": d.get("metadata", {})} for i, d in enumerate(documents)]
        request = RerankRequest(query=query, passages=passages)
        results = self._model.rerank(request)
        
        reranked = []
        for i, r in enumerate(results[:top_k]):
            orig_doc = documents[r["id"]]
            reranked.append(RerankResult(
                text=orig_doc["text"],
                original_score=orig_doc.get("score", 0.0),
                rerank_score=r["score"],
                metadata=orig_doc.get("metadata", {}),
                rank=i+1
            ))
        return reranked


def benchmark_reranker(reranker, query: str, documents: list[dict], n_runs: int = 5) -> dict:
    """Benchmark latency over n_runs."""
    times = []
    
    # Warmup
    reranker.rerank(query, documents)
    
    for _ in range(n_runs):
        start = time.perf_counter()
        reranker.rerank(query, documents)
        times.append((time.perf_counter() - start) * 1000)
        
    return {
        "avg_ms": sum(times) / len(times),
        "min_ms": min(times),
        "max_ms": max(times)
    }


if __name__ == "__main__":
    query = "Nhân viên được nghỉ phép bao nhiêu ngày?"
    docs = [
        {"text": "Nhân viên được nghỉ 12 ngày/năm.", "score": 0.8, "metadata": {}},
        {"text": "Mật khẩu thay đổi mỗi 90 ngày.", "score": 0.7, "metadata": {}},
        {"text": "Thời gian thử việc là 60 ngày.", "score": 0.75, "metadata": {}},
    ]
    reranker = CrossEncoderReranker()
    for r in reranker.rerank(query, docs):
        print(f"[{r.rank}] {r.rerank_score:.4f} | {r.text}")
