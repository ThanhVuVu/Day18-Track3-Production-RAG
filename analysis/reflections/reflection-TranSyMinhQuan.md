# Individual Reflection — Lab 18

**Tên:** Trần Sỹ Minh Quân
**Module phụ trách:** M2 - Hybrid Search

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M2 - Hybrid Search (BM25 + Dense Search)
- Các hàm/class chính đã viết: `BM25Search`, `DenseSearch`, `HybridSearch`, `reciprocal_rank_fusion` (RRF)
- Số tests pass: 10/10 (M2 tests)

## 2. Kiến thức học được

- Khái niệm mới nhất: Thuật toán Reciprocal Rank Fusion (RRF) để kết hợp kết quả từ nhiều bộ máy tìm kiếm khác nhau.
- Điều bất ngờ nhất: BM25 (tìm kiếm từ khóa) vẫn cực kỳ mạnh mẽ với tiếng Việt, đôi khi kết quả còn tốt hơn cả vector search nếu câu hỏi chứa danh từ riêng.
- Kết nối với bài giảng: Slide "Hybrid Search & RRF" - giải thích cách cân bằng giữa keyword match và semantic match.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Việc phân đoạn từ (tokenization) tiếng Việt cho BM25 không đồng nhất dẫn đến kết quả tìm kiếm kém.
- Cách giải quyết: Tích hợp thư viện `underthesea` để thực hiện word segmentation chuẩn trước khi đưa vào BM25.
- Thời gian debug: 3 giờ.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Thử nghiệm thay đổi hệ số `k` trong công thức RRF để xem nó ảnh hưởng thế nào đến độ ưu tiên của Vector Search.
- Module nào muốn thử tiếp: M3 - Reranking để học cách lọc kết quả sau khi hybrid search.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
