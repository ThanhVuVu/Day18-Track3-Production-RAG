# Group Report — Lab 18

**Nhóm:** Nhóm 1 (Production RAG)
**Ngày:** 04/05/2026

## Thành viên & Module

| Tên | Module | Hoàn thành | Tests pass |
|-----|--------|-----------|-----------|
| Vũ Như Đức | M1: Chunking | ✅ | 100% |
| Trần Sỹ Minh Quân | M2: Search | ✅ | 100% |
| Nguyễn Như Giáp | M3: Reranking | ✅ | 100% |
| Lương Hữu Thành | M4: Evaluation | ✅ | 100% |
| Nguyễn Tiến Thắng | M5: Enrichment | ✅ | 100% |
| Vũ Phúc Thành | Editor & Finalizer | ✅ | 100% |

## Kết quả

| Metric | Naive | Production | Δ |
|--------|-------|-----------|---|
| Faithfulness | 1.00 | 0.88 | -0.12 |
| Answer Relevancy | 0.00 | 0.35 | +0.35 |
| Context Precision | 1.00 | 0.96 | -0.04 |
| Context Recall | 1.00 | 1.00 | 0.00 |

## Key Findings

1. **Biggest improvement:** Hệ thống Production giúp Answer Relevancy tăng từ 0.0 lên 0.35 nhờ việc sử dụng LLM để tổng hợp câu trả lời thay vì chỉ copy-paste văn bản thô như bản Naive.
2. **Trade-off:** Điểm Faithfulness giảm nhẹ (từ 1.0 xuống 0.88) do LLM đôi khi tự diễn giải lại ý của tài liệu, tuy nhiên điều này giúp câu trả lời tự nhiên hơn cho người dùng.
3. **Retrieval Stability:** Nhờ Hybrid Search và Reranking, Context Precision và Recall luôn duy trì ở mức cực cao (>0.95), đảm bảo LLM luôn có đủ dữ liệu đúng để trả lời.

## Thách thức & Giải pháp

- **Thách thức:** API NVIDIA thường xuyên bị giới hạn tốc độ (Rate Limit 429).
- **Giải pháp:** Nhóm đã tối ưu hóa Module M4 bằng cách sử dụng model 8B nhẹ hơn và cấu hình `max_workers=4` kết hợp timeout 300s để quá trình đánh giá diễn ra ổn định và nhanh chóng.
