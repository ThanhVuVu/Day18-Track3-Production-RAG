# Individual Reflection — Lab 18

**Tên:** Nguyễn Như Giáp
**Module phụ trách:** M3 - Reranking

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M3 - Reranking Pipeline
- Các hàm/class chính đã viết: `CrossEncoderReranker`, `FlashrankReranker`, `benchmark_reranker`
- Số tests pass: 6/6 (M3 tests)

## 2. Kiến thức học được

- Khái niệm mới nhất: Sự khác biệt giữa Bi-Encoder (dùng để search nhanh) và Cross-Encoder (dùng để rerank chính xác).
- Điều bất ngờ nhất: Reranking tốn nhiều thời gian hơn tìm kiếm rất nhiều (latency cao), vì vậy chỉ nên rerank một tập nhỏ (ví dụ top 20).
- Kết nối với bài giảng: Slide "The Reranking Step" - giải thích về phễu lọc thông tin trong RAG.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Model Cross-Encoder khá nặng, làm tăng latency của hệ thống lên mức không chấp nhận được khi chạy trên CPU.
- Cách giải quyết: Triển khai thêm `FlashrankReranker` như một tùy chọn thay thế nhẹ hơn và tối ưu hóa số lượng document đưa vào rerank.
- Thời gian debug: 2.5 giờ.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Sử dụng các model reranker đã được quantized để chạy nhanh hơn trên máy cá nhân.
- Module nào muốn thử tiếp: M2 - Search để hiểu sâu hơn về cách layer tìm kiếm đầu tiên hoạt động.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
