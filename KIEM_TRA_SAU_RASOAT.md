# Báo cáo rà soát bổ sung — Nông Nghiệp Xanh

## Đã sửa trong vòng rà soát này

- Gỡ hai endpoint thử nghiệm mật mã `/auth/random-test` và `/auth/crypto-test` khỏi `worker.js`.
- Gia cố WebView: tắt mixed content, truy cập `content://`, truy cập file URL chéo nguồn và cửa sổ tự mở; chặn trang ngoài chạy bên trong WebView có cầu nối Android, chuyển liên kết HTTP/HTTPS ra trình duyệt hệ thống.
- Đồng bộ tên ứng dụng hiển thị thành `Nông Nghiệp Xanh`.
- Khi mở lại ứng dụng, khôi phục tọa độ thời tiết đã lưu vào ô nhập và hiển thị nhãn vị trí; kiểm tra phạm vi vĩ độ/kinh độ khi nhập dữ liệu sao lưu.
- Dọn các tệp rác do lệnh terminal và các bản HTML cũ khỏi thư mục asset của APK.
- Thêm `verify-project.sh` và bước kiểm tra mã nguồn trước khi workflow build APK chạy.

## Kiểm tra đã chạy

- Cú pháp JavaScript nhúng trong `index.html`: đạt.
- Cú pháp `worker.js` và `auth.js`: đạt.
- XML `AndroidManifest.xml`: đạt.
- 10 đích `showPage(...)` được tham chiếu trong HTML đều khớp ID phần giao diện.
- Hai endpoint thử nghiệm mật mã không còn trong Worker.

## Chưa xác nhận

- Chưa biên dịch APK trong môi trường rà soát vì không có Android SDK/Gradle được cấu hình.
- Chưa chạy kiểm thử tương tác trên thiết bị Android thật; quyền GPS, thông báo, tải bản đồ và chọn ảnh cần xác nhận trên điện thoại.
- Worker chưa tự triển khai lên Cloudflare. AI yêu cầu binding `AI`, quyền dùng mô hình và cấu hình D1 phù hợp; mã nguồn sửa đổi không tự cập nhật máy chủ đang chạy.
- Tên xã/huyện/tỉnh phụ thuộc dịch vụ reverse-geocoding và có thể không trùng hoàn toàn với cách gọi hành chính tại địa phương. Dự báo mưa là mô hình dự báo, không phải đo mưa thực tế tại từng thửa ruộng.
