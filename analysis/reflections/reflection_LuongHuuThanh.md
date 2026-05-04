# Individual Reflection — Lab 18

**Tên:** Phạm Thị D  
**Module phụ trách:** M4 - RAGAS Evaluation

---

## 1. Đóng góp kỹ thuật

- Module đã implement: M4 - Evaluation & Failure Analysis
- Các hàm/class chính đã viết: `evaluate_ragas`, `analyze_failures`, `save_report`, `safe_get`
- Số tests pass: 5/5 (M4 tests)

## 2. Kiến thức học được

- Khái niệm mới nhất: RAGAS metrics (Faithfulness, Relevancy, Precision, Recall) và cách dùng LLM làm "giám khảo" (LLM-as-a-judge).
- Điều bất ngờ nhất: RAGAS có thể phát hiện ra lỗi "ảo giác" (hallucination) mà nếu đọc bằng mắt thường đôi khi chúng ta sẽ bỏ sót.
- Kết nối với bài giảng: Slide "Evaluating RAG with RAGAS" - quy trình đánh giá không cần ground truth label (hoặc có ground truth).

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: API NVIDIA thường xuyên bị lỗi 429 (Too Many Requests) do Ragas gửi quá nhiều request song song.
- Cách giải quyết: Cấu hình lại `RunConfig` với `max_workers=1` và tăng `timeout` lên 300s, đồng thời viết hàm `safe_get` để xử lý các giá trị `NaN`.
- Thời gian debug: 4 giờ.

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Tự xây dựng thêm một vài custom metrics dựa trên nhu cầu riêng của doanh nghiệp thay vì chỉ dùng 4 metric mặc định.
- Module nào muốn thử tiếp: M5 - Enrichment vì chất lượng evaluation phụ thuộc rất nhiều vào chất lượng bối cảnh đầu vào.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
