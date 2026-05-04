# Individual Reflection — Lab 18

**Tên:** Vũ Phúc Thành  
**Module phụ trách:** Editor & Finalizer (Tổng hợp & Hoàn thiện báo cáo)

---

## 1. Đóng góp kỹ thuật

- Module đã implement: Tổng hợp kết quả từ các module M1-M5, biên tập Failure Analysis và Group Report.
- Các hàm/class chính đã viết: Quản lý cấu trúc thư mục báo cáo, đối soát dữ liệu giữa Naive Baseline và Production Pipeline.
- Số tests pass: 100% (Đảm bảo toàn bộ pipeline chạy thông suốt trước khi nộp).

## 2. Kiến thức học được

- Khái niệm mới nhất: Quy trình đánh giá RAG toàn diện (End-to-End Evaluation) và cách phân tích lỗi dựa trên Error Tree.
- Điều bất ngờ nhất: Việc tối ưu hóa model (từ 70B xuống 8B) và tăng số lượng luồng (max_workers) có thể cải thiện tốc độ đánh giá gấp nhiều lần mà vẫn giữ được độ chính xác cần thiết.
- Kết nối với bài giảng: Slide "RAG Evaluation Workflow" - cách thức tổ chức một dự án RAG chuyên nghiệp từ khâu tiền xử lý đến khâu báo cáo.

## 3. Khó khăn & Cách giải quyết

- Khó khăn lớn nhất: Kết quả đánh giá bị lỗi NaN do giới hạn của API NVIDIA làm hỏng bảng báo cáo tổng hợp.
- Cách giải quyết: Phối hợp cùng nhóm M4 để viết lại logic tính toán trung bình (manual average), bỏ qua các giá trị lỗi để có báo cáo trung thực nhất.
- Thời gian debug: 4 giờ (phần lớn là chờ chạy lại các bộ test).

## 4. Nếu làm lại

- Sẽ làm khác điều gì: Thiết lập hệ thống CI/CD đơn giản để tự động chạy đánh giá mỗi khi có thành viên cập nhật code module mới.
- Module nào muốn thử tiếp: Module M5 - Enrichment vì bối cảnh dữ liệu là "trái tim" của mọi hệ thống RAG.

## 5. Tự đánh giá

| Tiêu chí | Tự chấm (1-5) |
|----------|---------------|
| Hiểu bài giảng | 5 |
| Code quality | 5 |
| Teamwork | 5 |
| Problem solving | 5 |
