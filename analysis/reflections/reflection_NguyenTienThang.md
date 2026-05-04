# Individual Reflection — Lab 18

**Tên:** Nguyễn Tiến Thắng
**Module phụ trách:** M5 - Enrichment Pipeline

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M5 - Chunk Enrichment (Contextual Prepend, HyQA, Metadata)
- Các hàm/class chính đã viết: `contextual_prepend` (LLM-based), `generate_hypothesis_questions`, `extract_metadata`, `enrich_chunks`
- Số tests pass: 8/8 (M5 tests)

## 2. Kiến thức học được

- Khái niệm mới nhất: Contextual Retrieval (theo bài blog của Anthropic) - giúp giảm 49% lỗi retrieval bằng cách thêm bối cảnh cho mỗi chunk.
- Điều bất ngờ nhất: Việc thêm 1-2 câu bối cảnh vào đầu mỗi chunk có tác động cực lớn đến khả năng tìm kiếm chính xác, vượt xa các thuật toán tìm kiếm phức tạp.
- Kết nối với bài giảng: Slide "Data Enrichment for RAG" - các bước xử lý dữ liệu trước khi đưa vào database.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Chi phí API và thời gian index tăng lên đáng kể khi phải gọi LLM cho từng chunk văn bản.
- Cách giải quyết: Chỉ thực hiện enrichment cho các tài liệu quan trọng và sử dụng caching (hoặc lưu kết quả làm giàu ra file) để không phải chạy lại nhiều lần.
- Thời gian debug: 3 giờ.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Thử nghiệm thêm việc tạo hình ảnh mô tả (image captioning) cho các tài liệu có chứa biểu đồ để làm giàu dữ liệu đa phương thức.
- Module nào muốn thử tiếp: M1 - Chunking để kết hợp sâu hơn giữa cấu trúc văn bản và làm giàu dữ liệu.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
