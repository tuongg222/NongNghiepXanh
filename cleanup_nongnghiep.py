from pathlib import Path
from datetime import datetime
import re
import json
import shutil
import sys

html = Path("app/src/main/assets/index.html")
worker = Path("worker.js")

if not html.is_file() or not worker.is_file():
    sys.exit("LỖI: Không tìm thấy index.html hoặc worker.js. Chưa sửa gì.")

h = html.read_text(encoding="utf-8")
w = worker.read_text(encoding="utf-8")

# Kiểm tra các dấu mốc bắt buộc trước khi chỉnh sửa.
checks = [
    ("nút menu kinh doanh", 'showPage(\'business\',this);calculateBusiness()'),
    ("trang kinh doanh", '<section id="business" class="page">'),
    ("hàm mặc định kinh doanh", "const bizDefaults = {"),
    ("hàm showPage", "function showPage(id,btn)"),
    ("lời gọi tải kế hoạch", "loadBusinessPlan();"),
    ("lời gọi tính toán", "calculateBusiness();"),
]
for label, marker in checks:
    if marker not in h:
        sys.exit(f"LỖI: Không tìm thấy {label}. Chưa sửa gì.")

if 'role: "system"' not in w or "Bạn hỗ trợ nông dân Việt Nam" not in w:
    sys.exit("LỖI: Không tìm thấy prompt AI dự kiến. Chưa sửa gì.")

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
hb = html.with_name(html.name + f".before-cleanup-{stamp}.bak")
wb = worker.with_name(worker.name + f".before-ai-cleanup-{stamp}.bak")
shutil.copy2(html, hb)
shutil.copy2(worker, wb)

# Gỡ nút menu kinh doanh.
h = re.sub(
    r'^[ \t]*<button onclick="showPage\(\'business\',this\);calculateBusiness\(\)">.*?</button>[ \t]*\n?',
    '',
    h,
    count=1,
    flags=re.M
)

# Gỡ toàn bộ trang business, từ section mở đến section đóng tương ứng.
start = h.index('<section id="business" class="page">')
end = h.index('</section>', start) + len('</section>')
# Trang có các thẻ div nhưng chỉ một section ngoài cùng.
h = h[:start] + h[end:]

# Gỡ các hàm business, giữ nguyên function showPage.
start = h.index("const bizDefaults = {")
end = h.index("function showPage(id,btn)", start)
h = h[:start] + h[end:]

# Gỡ khóa kế hoạch kinh doanh khỏi danh sách sao lưu và bộ kiểm tra nhập.
h = h.replace('"nx_disease_photos", "nx_weather_daily", "nx_business_plan",',
              '"nx_disease_photos", "nx_weather_daily",')
h = re.sub(
    r'\s*nx_business_plan:\s*function\(v\)\s*\{\s*return v !== null && typeof v === "object" && !Array\.isArray\(v\);\s*\},?',
    '',
    h,
    count=1
)

# Bỏ lời gọi khởi tạo không còn cần thiết ở cuối file.
h = h.replace("\nloadBusinessPlan();\ncalculateBusiness();", "")

# Cải thiện hướng dẫn AI: tự nhiên, tránh lặp và độ dài phù hợp.
new_prompt = (
    "Bạn là trợ lý nông nghiệp hỗ trợ nông dân Việt Nam đánh giá sơ bộ cây lúa qua ảnh. "
    "Trả lời bằng tiếng Việt tự nhiên, rõ ràng, gần gũi và đi thẳng vào câu hỏi. "
    "Không lặp lại câu hỏi, không lặp ý, câu hoặc đoạn; không nhắc lại cùng một khuyến nghị bằng nhiều cách. "
    "Ưu tiên câu ngắn, từ ngữ dễ hiểu; chỉ dùng tiêu đề hoặc danh sách khi giúp dễ đọc. "
    "Thông thường trả lời vừa đủ, khoảng 4-8 gạch đầu dòng; chỉ phân tích dài khi người dùng yêu cầu. "
    "Nêu riêng dấu hiệu thực sự nhìn thấy và nguyên nhân chỉ mới nghi ngờ. "
    "Không khẳng định chắc chắn bệnh chỉ từ ảnh, không bịa tên bệnh, mức độ tin cậy hoặc tên thuốc. "
    "Nếu ảnh chưa rõ, nói chính xác thông tin còn thiếu và hỏi tối đa 2 câu cần thiết. "
    "Đưa ra việc nên làm ngay, cách kiểm tra ngoài ruộng và cách theo dõi; ưu tiên IPM, vệ sinh đồng ruộng, nước và dinh dưỡng phù hợp. "
    "Không tự chỉ định hoạt chất, liều lượng hay pha trộn thuốc khi chưa đủ căn cứ. "
    "Nếu cần thuốc, khuyên hỏi cán bộ bảo vệ thực vật và làm đúng nhãn, đồ bảo hộ, thời gian cách ly. "
    "Chỉ nhắc phòng ngừa khi phù hợp; tránh lặp lại nội dung đã nói. "
    "Khi không chắc, hãy thành thật nói rõ giới hạn và đề nghị thông tin bổ sung cụ thể."
)

# Chỉ thay nội dung system prompt, không đụng phần xác thực hay API.
pattern = r'(role:\s*"system",\s*content:\s*)[\s\S]*?(\s*\n\s*\},\s*\{\s*\n\s*role:\s*"user")'
w2, count = re.subn(
    pattern,
    lambda m: m.group(1) + json.dumps(new_prompt, ensure_ascii=False) + m.group(2),
    w,
    count=1
)
if count != 1:
    sys.exit(
        "LỖI: Không thay được prompt theo cấu trúc dự kiến. "
        "Đã tạo bản sao lưu; tệp gốc chưa được ghi."
    )

# Kiểm tra dấu mốc sau sửa trước khi ghi.
if 'id="business"' in h or "function calculateBusiness()" in h:
    sys.exit("LỖI: Vẫn còn phần business. Tệp gốc chưa được ghi.")
if "loadBusinessPlan();" in h or "calculateBusiness();" in h:
    sys.exit("LỖI: Vẫn còn lời gọi business. Tệp gốc chưa được ghi.")
if "role: \"user\"" not in w2 or "Không lặp lại câu hỏi" not in w2:
    sys.exit("LỖI: Kiểm tra prompt AI không đạt. Tệp gốc chưa được ghi.")

# Ghi cả hai tệp sau khi tất cả kiểm tra đã qua.
html.write_text(h, encoding="utf-8")
worker.write_text(w2, encoding="utf-8")

print("ĐÃ SỬA:")
print("- Đã gỡ trang và menu Thị trường & Kinh doanh.")
print("- Đã gỡ hàm tính toán và khóa sao lưu riêng của trang.")
print("- Đã tinh gọn prompt AI để giảm lặp từ, lặp ý và trả lời dài dòng.")
print(f"- Bản sao lưu HTML: {hb}")
print(f"- Bản sao lưu Worker: {wb}")
