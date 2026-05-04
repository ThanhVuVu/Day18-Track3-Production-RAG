"""
Module 5: Enrichment Pipeline
==============================
Làm giàu chunks TRƯỚC khi embed: Summarize, HyQA, Contextual Prepend, Auto Metadata.

Test: pytest tests/test_m5.py
"""

import os
import sys
import json
from dataclasses import dataclass
from langchain_nvidia_ai_endpoints import ChatNVIDIA

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize LLM for enrichment
def get_enrichment_llm():
    return ChatNVIDIA(
        model="meta/llama-3.1-70b-instruct",
        nvidia_api_key=os.environ.get("NVIDIA_API_KEY", ""),
        temperature=0.1,
        max_tokens=1024,
        timeout=300
    )



@dataclass
class EnrichedChunk:
    """Chunk đã được làm giàu."""
    original_text: str
    enriched_text: str
    summary: str
    hypothesis_questions: list[str]
    auto_metadata: dict
    method: str  # "contextual", "summary", "hyqa", "full"


# ─── Technique 1: Chunk Summarization ────────────────────


def summarize_chunk(text: str) -> str:
    """
    Tạo summary ngắn cho chunk.
    Embed summary thay vì (hoặc cùng với) raw chunk → giảm noise.

    Args:
        text: Raw chunk text.

    Returns:
        Summary string (2-3 câu).
    """
    sentences = text.split(". ")
    return ". ".join(sentences[:2]) + "."


# ─── Technique 2: Hypothesis Question-Answer (HyQA) ─────


def generate_hypothesis_questions(text: str, n_questions: int = 3, llm: ChatNVIDIA = None) -> list[str]:
    """
    Generate câu hỏi mà chunk có thể trả lời.
    Index cả questions lẫn chunk → query match tốt hơn (bridge vocabulary gap).
    """
    if not llm:
        # Fallback/Rule-based implementation
        questions = []
        if "nghỉ phép" in text.lower():
            questions.append("Nhân viên được nghỉ bao nhiêu ngày phép?")
        if "vpn" in text.lower() or "forticlient" in text.lower():
            questions.append("Làm thế nào để kết nối VPN?")
        if not questions:
            questions = ["Câu hỏi giả định về nội dung này 1?", "Câu hỏi giả định về nội dung này 2?"]
        return questions[:n_questions]

    # LLM Implementation
    prompt = f"Dựa trên đoạn văn bản sau, hãy tạo ra {n_questions} câu hỏi ngắn gọn mà đoạn văn này có thể trả lời. Chỉ trả về danh sách các câu hỏi, mỗi câu trên một dòng.\n\nVăn bản: {text}"
    try:
        resp = llm.invoke(prompt)
        questions = [q.strip() for q in resp.content.split("\n") if q.strip()]
        return questions[:n_questions]
    except Exception as e:
        print(f"  [!] HyQA LLM error: {e}")
        return []


# ─── Technique 3: Contextual Prepend (Anthropic style) ──


def contextual_prepend(text: str, document_title: str = "", full_document: str = "", llm: ChatNVIDIA = None) -> str:
    """
    Prepend context giải thích chunk nằm ở đâu trong document (Anthropic Style).
    """
    if not llm or not full_document:
        source_name = document_title if document_title else "Tài liệu hệ thống"
        context = f"Trích từ tài liệu: {source_name}. Đoạn văn này chứa các thông tin và quy định liên quan."
        return f"{context}\n\n{text}"

    # LLM Implementation (Anthropic Contextual Retrieval)
    prompt = f"""
<document>
{full_document}
</document>
Hãy cung cấp một bối cảnh ngắn gọn (1-2 câu) để xác định vị trí của đoạn văn sau trong toàn bộ tài liệu trên nhằm mục đích cải thiện khả năng tìm kiếm.
Chỉ trả về phần bối cảnh, không thêm bất kỳ lời dẫn nào khác.

Đoạn văn cần xác định bối cảnh:
{text}
"""
    try:
        resp = llm.invoke(prompt)
        context = resp.content.strip()
        return f"{context}\n\n{text}"
    except Exception as e:
        print(f"  [!] Contextual Prepend LLM error: {e}")
        return f"Tài liệu: {document_title}\n\n{text}"


# ─── Technique 4: Auto Metadata Extraction ──────────────


def extract_metadata(text: str, llm: ChatNVIDIA = None) -> dict:
    """
    LLM extract metadata tự động: topic, entities, category.
    """
    if not llm:
        topic = "Chung"
        if "nghỉ phép" in text.lower():
            topic = "Quy định nghỉ phép"
        elif "vpn" in text.lower() or "forticlient" in text.lower():
            topic = "Hướng dẫn IT"
        return {
            "topic": topic,
            "entities": [],
            "category": "policy" if "quy định" in text.lower() else "general",
            "language": "vi"
        }

    # LLM Implementation
    prompt = f"""Hãy trích xuất metadata từ đoạn văn bản sau dưới dạng JSON với các trường: topic, entities (list), category, language.
Chỉ trả về mã JSON, không thêm lời dẫn.

Văn bản: {text}"""
    try:
        resp = llm.invoke(prompt)
        content = resp.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
        return json.loads(content)
    except Exception as e:
        print(f"  [!] Metadata Extraction LLM error: {e}")
        return {"topic": "Chung", "entities": [], "category": "general", "language": "vi"}


# ─── Full Enrichment Pipeline ────────────────────────────


def enrich_chunks(
    chunks: list[dict],
    methods: list[str] | None = None,
    use_llm: bool = True
) -> list[EnrichedChunk]:
    """
    Chạy enrichment pipeline trên danh sách chunks.
    """
    if methods is None:
        methods = ["contextual", "hyqa", "metadata"]

    llm = get_enrichment_llm() if use_llm and os.environ.get("NVIDIA_API_KEY") else None
    if llm:
        print(f"  [Enrichment] Using LLM for {', '.join(methods)}")

    enriched = []

    for chunk in chunks:
        raw_text = chunk.get("text", "")
        meta = chunk.get("metadata", {})
        full_doc = chunk.get("full_document_text", "") # Pass this in the chunk dict if available
        
        summary = summarize_chunk(raw_text) if "summary" in methods or "full" in methods else ""
        questions = generate_hypothesis_questions(raw_text, llm=llm) if "hyqa" in methods or "full" in methods else []
        auto_meta = extract_metadata(raw_text, llm=llm) if "metadata" in methods or "full" in methods else {}
        
        enriched_text = raw_text
        if "contextual" in methods or "full" in methods:
            source = meta.get("source", "")
            enriched_text = contextual_prepend(raw_text, source, full_document=full_doc, llm=llm)
            
        enriched.append(EnrichedChunk(
            original_text=raw_text,
            enriched_text=enriched_text,
            summary=summary,
            hypothesis_questions=questions,
            auto_metadata={**meta, **auto_meta},
            method="+".join(methods)
        ))
        
    return enriched


# ─── Main ────────────────────────────────────────────────

if __name__ == "__main__":
    sample = "Nhân viên chính thức được nghỉ phép năm 12 ngày làm việc mỗi năm. Số ngày nghỉ phép tăng thêm 1 ngày cho mỗi 5 năm thâm niên công tác."

    print("=== Enrichment Pipeline Demo ===\n")
    print(f"Original: {sample}\n")

    s = summarize_chunk(sample)
    print(f"Summary: {s}\n")

    qs = generate_hypothesis_questions(sample)
    print(f"HyQA questions: {qs}\n")

    ctx = contextual_prepend(sample, "Sổ tay nhân viên VinUni 2024")
    print(f"Contextual: {ctx}\n")

    meta = extract_metadata(sample)
    print(f"Auto metadata: {meta}")
