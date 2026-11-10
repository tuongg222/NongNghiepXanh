from pathlib import Path
from datetime import datetime
import shutil

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

# Kiểm tra trước khi sửa
required = [
    "import 'package:flutter/material.dart';",
    "bool registering=false",
    "// Switch login/register",
    "Widget glass(",
]
for marker in required:
    if marker not in s:
        print("❌ Không tìm thấy:", marker)
        raise SystemExit("Dừng, không sửa file.")

if "LOGIN_NETWORK_DIAGNOSTIC" in s:
    raise SystemExit("⚠️ Đã chèn chẩn đoán trước đó.")

backup = p.with_suffix(
    ".dart.bak_" + datetime.now().strftime("%Y%m%d_%H%M%S")
)
shutil.copy2(p, backup)

# Imports
s = s.replace(
    "import 'package:flutter/material.dart';",
    "import 'dart:io';\n"
    "import 'package:flutter/material.dart';\n"
    "import '../services/api_service.dart';",
    1
)

# State
state_marker = "bool registering=false"
s = s.replace(
    state_marker,
    state_marker + "\n  bool diagnosing = false;\n  String? diagnostic;",
    1
)

# Hàm kiểm tra mạng
method_marker = "  Widget glass("
method = r"""
  // LOGIN_NETWORK_DIAGNOSTIC
  Future<void> checkServer() async {
    setState(() {
      diagnosing = true;
      diagnostic = 'Đang kiểm tra DNS...';
    });

    final host = Uri.parse(ApiService.workerBase).host;

    try {
      final addresses = await InternetAddress.lookup(host)
          .timeout(const Duration(seconds: 12));

      if (addresses.isEmpty) {
        throw const SocketException('DNS không trả về địa chỉ IP');
      }

      if (!mounted) return;
      setState(() => diagnostic =
          '✅ DNS OK: ${addresses.map((e) => e.address).join(", ")}'
          '\nĐang kiểm tra HTTPS và Worker...');

      final result = await ApiService.health()
          .timeout(const Duration(seconds: 20));

      if (!mounted) return;
      setState(() => diagnostic =
          '✅ DNS: OK\n'
          '✅ HTTPS: OK\n'
          '✅ Worker API: OK\n'
          'AI: ${result["aiConnected"] == true ? "Đã kết nối" : "Chưa kết nối"}'
          '\n\nMáy chủ hoạt động bình thường.');
    } on SocketException catch (e) {
      if (!mounted) return;
      setState(() => diagnostic =
          '❌ DNS / mạng lỗi:\n${e.message}\n\n'
          'Chi tiết: $e');
    } on Exception catch (e) {
      if (!mounted) return;
      setState(() => diagnostic =
          '❌ HTTPS / API lỗi:\n$e');
    } catch (e) {
      if (!mounted) return;
      setState(() => diagnostic = '❌ Lỗi không xác định:\n$e');
    } finally {
      if (mounted) setState(() => diagnosing = false);
    }
  }

"""
if s.count(method_marker) != 1:
    raise SystemExit("Marker hàm glass không duy nhất.")
s = s.replace(method_marker, method + method_marker, 1)

# Nút + kết quả chẩn đoán trước phần chuyển đăng nhập/đăng ký
ui_marker = "                                  // Switch login/register"
ui = r"""
                                  // LOGIN_NETWORK_DIAGNOSTIC
                                  SizedBox(
                                    width: double.infinity,
                                    child: OutlinedButton.icon(
                                      onPressed: diagnosing ? null : checkServer,
                                      icon: diagnosing
                                          ? const SizedBox(
                                              width: 16,
                                              height: 16,
                                              child: CircularProgressIndicator(
                                                strokeWidth: 2,
                                                color: Color(0xFFB9FFD8),
                                              ),
                                            )
                                          : const Icon(Icons.wifi_tethering),
                                      label: Text(diagnosing
                                          ? 'ĐANG KIỂM TRA...'
                                          : 'KIỂM TRA KẾT NỐI MÁY CHỦ'),
                                      style: OutlinedButton.styleFrom(
                                        foregroundColor: Colors.white,
                                        side: BorderSide(
                                          color: Colors.white.withOpacity(.35),
                                        ),
                                      ),
                                    ),
                                  ),
                                  if (diagnostic != null) ...[
                                    const SizedBox(height: 10),
                                    Container(
                                      width: double.infinity,
                                      padding: const EdgeInsets.all(12),
                                      decoration: BoxDecoration(
                                        color: Colors.black.withOpacity(.18),
                                        borderRadius: BorderRadius.circular(12),
                                      ),
                                      child: SelectableText(
                                        diagnostic!,
                                        style: const TextStyle(
                                          color: Color(0xFFB9FFD8),
                                          fontSize: 12,
                                        ),
                                      ),
                                    ),
                                  ],
                                  const SizedBox(height: 10),

"""
if s.count(ui_marker) != 1:
    raise SystemExit("Marker nút chuyển login không duy nhất.")
s = s.replace(ui_marker, ui + ui_marker, 1)

p.write_text(s)
print("✅ Đã chèn chẩn đoán mạng.")
print("📦 Backup:", backup)
