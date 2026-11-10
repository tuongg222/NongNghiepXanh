from pathlib import Path

p = Path("lib/services/auth_service.dart")
s = p.read_text()

if "SocketException" in s:
    print("AuthService đã có xử lý SocketException.")
    raise SystemExit(0)

s = s.replace(
    "import 'dart:convert';",
    "import 'dart:convert';\nimport 'dart:io';"
)

s = s.replace(
    """    final response = await http.post(
      Uri.parse('${ApiService.workerBase}$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    ).timeout(const Duration(seconds: 30));""",
    """    http.Response response;
    try {
      response = await http.post(
        Uri.parse('${ApiService.workerBase}$endpoint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      ).timeout(const Duration(seconds: 30));
    } on SocketException {
      throw Exception('Không thể kết nối máy chủ. Hãy kiểm tra Internet hoặc DNS.');
    } on HttpException {
      throw Exception('Lỗi kết nối HTTP.');
    } on FormatException {
      throw Exception('Dữ liệu máy chủ không hợp lệ.');
    } catch (e) {
      if (e.toString().contains('TimeoutException')) {
        throw Exception('Kết nối quá lâu. Vui lòng thử lại.');
      }
      rethrow;
    }"""
)

p.write_text(s)
print("Đã cập nhật xử lý lỗi mạng AuthService.")
