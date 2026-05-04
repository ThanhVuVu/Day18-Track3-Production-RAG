# Individual Reflection — Lab 18

**Tên:** Vũ Như Đức  
**Module phụ trách:** M1 - Chunking

---

## 1. Đóng góp kỹ thuật

- Module đã implement: Advanced Chunking Strategies cho M1, gồm semantic chunking, hierarchical chunking, structure-aware chunking và hàm so sánh các chiến lược.
- Các hàm/class chính đã viết: `Chunk`, `chunk_semantic()`, `chunk_hierarchical()`, `chunk_structure_aware()`, `compare_strategies()`.
- Số tests pass: 13/13.

## 2. Kiến thức học được

- Khái niệm mới nhất: Cách tách chunk theo ngữ nghĩa thay vì chỉ cắt theo độ dài, và cách parent-child retrieval giữ được cả precision lẫn context.
- Điều bất ngờ nhất: Hierarchical chunking giúp truy hồi chính xác hơn mà vẫn trả về ngữ cảnh đủ rộng cho LLM, nên phù hợp hơn baseline cho RAG production.
- Kết nối với bài giảng (slide nào): Slide về RAG chunking strategies, semantic search và parent-child retrieval.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Chỉnh ngưỡng similarity trong semantic chunking và kích thước parent/child sao cho vừa không cắt vỡ ý vừa không tạo chunk quá dài.
- Cách giải quyết: Kiểm tra đầu ra bằng test mẫu, so sánh với basic chunking, rồi tinh chỉnh threshold và logic chia parent-child để đảm bảo child luôn map đúng parent_id.
- Thời gian debug: Khoảng 2 giờ.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Tách phần tính similarity và cấu hình chunk size ra sớm hơn để dễ thử nghiệm nhiều chiến lược mà không phải sửa logic chính.
- Module nào muốn thử tiếp: M2 - Hybrid Search, vì nó nối trực tiếp với chunking để thấy rõ hiệu quả end-to-end của RAG.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
