# Nâng cấp AI chẩn đoán và hướng dẫn xử lý

## Đã sửa
- Cập nhật system prompt trong `worker.js` để yêu cầu kết quả có cấu trúc 8 phần: tóm tắt, dấu hiệu quan sát, nguyên nhân nghi ngờ và lý do, cách kiểm tra phân biệt, xử lý theo bước, việc không nên làm, phòng ngừa/theo dõi, thông tin cần bổ sung.
- Yêu cầu AI đưa ra bước an toàn có thể làm ngay ngay cả khi chưa đủ dữ kiện; không được chỉ hỏi thêm rồi dừng.
- Yêu cầu phân biệt điều quan sát được với giả thuyết; giải thích dấu hiệu ủng hộ/chưa phù hợp; giới hạn tối đa 3 câu hỏi bổ sung.
- Tăng giới hạn đầu ra lên `max_tokens: 1200` để giảm nguy cơ câu trả lời bị cụt khi có đủ các mục.
- Giữ nguyên endpoint `/diagnose`, cấu trúc response `{ ok, aiConnected, result }`, model đang cấu hình, luồng đăng nhập và giao diện lịch sử.

## Kiểm tra đã chạy
- `bash verify-project.sh`: PASS (HTML, JavaScript nhúng, AndroidManifest, worker.js, auth.js).
- `node --check worker.js`: PASS.

## Lưu ý triển khai
Đây là sửa mã nguồn. Để AI trên ứng dụng đang cài đặt nhận thay đổi, cần deploy `worker.js` đã sửa lên Cloudflare Workers (và đảm bảo binding `AI` cùng giấy phép model đã được cấu hình). Chưa thể xác nhận phản hồi AI thực tế hoặc build APK trong môi trường này vì không có quyền truy cập tài khoản Cloudflare và chưa chạy Android Gradle build.
