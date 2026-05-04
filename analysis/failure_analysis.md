# Failure Analysis — Lab 18

**Nhóm:** Nhóm 1 (Production RAG)
**Thành viên:** Vũ Như Đức → M1 · Trần Sỹ Minh Quân → M2 · Nguyễn Như Giáp → M3 · Lương Hữu Thành → M4 · Nguyễn Tiến Thắng → M5 · Thanh Vũ Vũ → Editor & Finalizer

## RAGAS Scores

| Metric | Naive Baseline | Production | Δ |
|--------|---------------|------------|---|
| Faithfulness | 1.00 | 0.88 | -0.12 |
| Answer Relevancy | 0.00 | 0.35* | +0.35 |
| Context Precision | 1.00 | 0.96 | -0.04 |
| Context Recall | 1.00 | 1.00 | 0.00 |

*\*Lưu ý: Điểm Answer Relevancy của Production thực tế trung bình ~0.35 (được tính thủ công từ per-question), điểm 0.0 ở aggregate là do lỗi tính toán trung bình khi gặp giá trị NaN từ API.*

## Bottom-5 Failures

### #1
- **Question:** Làm thế nào để tăng thêm số ngày nghỉ phép hàng năm?
- **Expected:** Cứ mỗi 5 năm làm việc, số ngày nghỉ phép sẽ được tăng thêm 1 ngày.
- **Got:** (Nội dung LLM tự chế thêm về các loại phép khác không có trong văn bản)
- **Worst metric:** Faithfulness (0.2)
- **Error Tree:** Output sai → Context đúng? (Có) → Query OK? (Có) → Root cause: LLM Hallucination (Ảo giác LLM) do temperature hoặc prompt chưa đủ chặt chẽ khiến nó tự suy diễn thêm các quy định không có trong tài liệu.
- **Suggested fix:** Tighten prompt template, giảm temperature xuống 0 tuyệt đối và thêm yêu cầu "Chỉ trả lời dựa trên context".

### #2
- **Question:** Nhân viên có bao nhiêu ngày nghỉ phép năm?
- **Expected:** Nhân viên chính thức có 12 ngày nghỉ phép năm.
- **Got:** Đoạn văn bản dài dòng về quy định nghỉ phép.
- **Worst metric:** Answer Relevancy (0.15)
- **Error Tree:** Output đúng? (Có) → Context đúng? (Có) → Query OK? (Có) → Root cause: Câu trả lời quá dài dòng và bao gồm cả các thông tin không cần thiết, làm loãng ý chính.
- **Suggested fix:** Cải thiện Prompt để LLM tập trung vào việc trả lời ngắn gọn, trực tiếp vào con số được hỏi.

### #3
- **Question:** Tôi muốn nghỉ vào thứ Tư, tôi phải báo muộn nhất là khi nào?
- **Expected:** Phải thông báo trước ít nhất 2 ngày làm việc (muộn nhất là thứ Hai).
- **Got:** Bạn cần báo trước 2 ngày.
- **Worst metric:** Answer Relevancy (0.19)
- **Error Tree:** Output đúng? (Có) → Context đúng? (Có) → Query OK? (Có) → Root cause: LLM chưa thực hiện bước suy luận từ "2 ngày trước" sang "thứ Hai" cho người dùng.
- **Suggested fix:** Thêm bước "Chain of Thought" vào prompt để LLM thực hiện suy luận logic thời gian.

### #4
- **Question:** Làm việc tại công ty 5 năm thì có bao nhiêu ngày phép?
- **Expected:** 13 ngày (12 ngày gốc + 1 ngày thâm niên).
- **Got:** 12 ngày.
- **Worst metric:** Answer Relevancy (0.20)
- **Error Tree:** Output sai → Context đúng? (Có) → Query OK? (Có) → Root cause: LLM bỏ sót thông tin về việc tăng thêm 1 ngày phép sau mỗi 5 năm.
- **Suggested fix:** Sử dụng Reranking để đưa đoạn văn về thâm niên lên vị trí cao hơn hoặc dùng Hybrid Search để bắt từ khóa "5 năm".

### #5
- **Question:** Sau bao lâu thì số ngày phép của tôi bắt đầu tăng lên?
- **Expected:** Sau mỗi 5 năm làm việc.
- **Got:** Thông tin chung về nghỉ phép.
- **Worst metric:** Answer Relevancy (0.21)
- **Error Tree:** Output đúng? (Một phần) → Context đúng? (Có) → Root cause: Answer chưa trả lời trực tiếp vào mốc thời gian "5 năm".
- **Suggested fix:** Cải thiện bối cảnh bằng Contextual Prepend để làm nổi bật quy định về thâm niên.

## Case Study (presentation)

**Question:** Làm thế nào để truy cập VPN từ xa?

**Error Tree walkthrough:**
1. Output đúng? → Đúng, LLM liệt kê đủ 4 bước (FortiClient, Server, Login, 2FA).
2. Context đúng? → Đúng, Hybrid Search đã tìm thấy chính xác file `sample_02.md`.
3. Query rewrite OK? → OK, HyQA đã tạo ra các câu hỏi tương tự giúp tăng recall.
4. Fix ở bước: Bước này hệ thống chạy hoàn hảo nhất nhờ có Hybrid Search kết hợp Reranking.

**Nếu có thêm 1 giờ:**
- Triển khai **GraphRAG** để xử lý các mối quan hệ phức tạp giữa các quy định.
- Tối ưu hóa **Latency** bằng cách sử dụng các model Quantized (GGUF) chạy local thay vì gọi API.
- Xây dựng bộ **Evaluation Dataset** lớn hơn (100+ câu hỏi) bằng LLM để đánh giá stress-test hệ thống.
