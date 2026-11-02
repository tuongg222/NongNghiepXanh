# Nông Nghiệp Xanh — bản cập nhật mã nguồn

## Các thay đổi chính
- Bỏ tọa độ thời tiết mặc định gần Cần Thơ để tránh hiển thị nhầm thời tiết vị trí thử nghiệm.
- Thêm nút lấy GPS cho thời tiết; lưu tọa độ đã chọn và thử tra cứu địa danh hành chính. Nếu dịch vụ địa danh không phản hồi, ứng dụng vẫn dùng tọa độ GPS.
- Bản đồ mở ở góc nhìn toàn Việt Nam nếu chưa có vị trí; có nút đưa bản đồ đến GPS/vị trí ruộng.
- Các ô lối tắt trên trang Tổng quan đã bấm được và chuyển đến đúng chức năng.
- Cảnh báo thời tiết xét cả lượng mưa dự kiến theo mm/ngày, không chỉ xác suất mưa.
- Sao lưu/khôi phục bổ sung vị trí thời tiết; dữ liệu nhập được kiểm tra định dạng trước khi ghi và có cơ chế hoàn tác khi ghi lỗi.
- Chẩn đoán ảnh AI gửi kèm giai đoạn lúa và mô tả triệu chứng do người trồng nhập để làm ngữ cảnh. AI vẫn chỉ hỗ trợ tham khảo.
- Workflow build chấp nhận giấy phép Android SDK theo cách phù hợp CI hơn.

## Kiểm tra mã nguồn

Cần Node.js và Python 3; chạy trước khi build:

```bash
./verify-project.sh
```

Script kiểm tra cú pháp JavaScript trong giao diện và Worker, cùng XML Manifest Android. Đây không thay thế build APK hoặc kiểm thử trên thiết bị thật.

## Build APK trên Termux
Mở thư mục dự án sau khi giải nén rồi chạy:

```bash
pkg update
pkg install openjdk-17 gradle unzip -y
cd NongNghiepXanh
```

Nếu Termux đã cài Android SDK và biến `ANDROID_HOME`/`ANDROID_SDK_ROOT` được cấu hình, chạy:

```bash
./verify-project.sh
gradle --no-daemon clean assembleDebug
```

APK sẽ nằm ở `app/build/outputs/apk/debug/app-debug.apk` nếu build thành công.

Nếu Termux chưa có Android SDK đầy đủ, cách ổn định hơn là đưa mã nguồn lên GitHub, vào **Actions → Build Nong Nghiep Xanh APK → Run workflow**, rồi tải artifact `NongNghiepXanh-debug-*` khi workflow xanh.

## Lưu ý
- Mã JavaScript trong trang và `worker.js` đã được kiểm tra cú pháp bằng Node.js; Android APK chưa được build trong môi trường kiểm tra này vì không có Android SDK/Gradle cài sẵn.
- Dịch vụ thời tiết cần Internet. Độ chính xác GPS phụ thuộc thiết bị và môi trường; tên xã/huyện/tỉnh là kết quả tra cứu địa danh, có thể thiếu hoặc khác cách gọi địa phương.
- Worker AI cần được triển khai riêng lên Cloudflare và cần cấu hình binding `AI`; nếu Cloudflare yêu cầu chấp nhận giấy phép mô hình, chủ dự án phải hoàn tất thao tác đó trong tài khoản Cloudflare.
