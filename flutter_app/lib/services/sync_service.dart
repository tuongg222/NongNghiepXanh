import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'auth_service.dart';
import 'api_service.dart';

class SyncService {
  static const Map<String, String> _keys = {
    'seasons': 'nx_seasons',
    'journal': 'nx_journal',
    'finance': 'nx_finance',
    'prices': 'nx_prices',
    'fields': 'nx_fields',
  };

  static Map<String, String> _headers() {
    final token = AuthService.token;
    if (token == null || token.isEmpty) {
      throw Exception('Bạn cần đăng nhập để đồng bộ.');
    }
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  static Future<Map<String, dynamic>> _getCloud() async {
    final response = await http.get(
      Uri.parse('${ApiService.workerBase}/data'),
      headers: _headers(),
    ).timeout(const Duration(seconds: 30));

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(body['error'] ?? 'Không tải được dữ liệu cloud.');
    }
    return Map<String, dynamic>.from(body['data'] ?? {});
  }

  static Future<void> _putCloud(String key, dynamic data) async {
    final response = await http.put(
      Uri.parse('${ApiService.workerBase}/data'),
      headers: _headers(),
      body: jsonEncode({'key': key, 'data': data}),
    ).timeout(const Duration(seconds: 30));

    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(body['error'] ?? 'Không lưu được dữ liệu $key.');
    }
  }

  /// Tự sao lưu một nhóm dữ liệu sau khi lưu local.
  /// Không đăng nhập hoặc lỗi mạng thì vẫn giữ dữ liệu trên máy.
  static Future<void> uploadKey(String key, dynamic data) async {
    if (AuthService.token == null || AuthService.token!.isEmpty) return;

    try {
      await _putCloud(key, data);
    } catch (e) {
      // Local đã lưu thành công; lỗi Cloud không làm mất dữ liệu.
      print('Cloud sync $key thất bại: $e');
    }
  }

  /// Đẩy toàn bộ dữ liệu hiện có trên máy lên Cloudflare.
  static Future<void> uploadAll() async {
    final prefs = await SharedPreferences.getInstance();
    for (final entry in _keys.entries) {
      final raw = prefs.getString(entry.value);
      if (raw == null) continue;
      await _putCloud(entry.key, jsonDecode(raw));
    }
  }

  /// Tải dữ liệu cloud về máy. Chỉ ghi những nhóm có trên cloud.
  static Future<void> downloadAll() async {
    final cloud = await _getCloud();
    final prefs = await SharedPreferences.getInstance();

    for (final entry in _keys.entries) {
      if (!cloud.containsKey(entry.key)) continue;
      await prefs.setString(entry.value, jsonEncode(cloud[entry.key]));
    }
  }

  /// Đồng bộ lúc khởi động nhưng không ghi đè dữ liệu đang có.
  static Future<void> syncOnStartup() async {
    if (AuthService.token == null || AuthService.token!.isEmpty) return;

    try {
      final cloud = await _getCloud();
      final prefs = await SharedPreferences.getInstance();

      for (final entry in _keys.entries) {
        final raw = prefs.getString(entry.value);
        final hasCloud = cloud.containsKey(entry.key);

        if (raw == null && hasCloud) {
          await prefs.setString(
            entry.value,
            jsonEncode(cloud[entry.key]),
          );
        } else if (raw != null && !hasCloud) {
          await _putCloud(entry.key, jsonDecode(raw));
        }
        // Cả local và cloud đều có: không tự ghi đè.
      }
    } catch (e) {
      print('Startup Cloud sync thất bại: $e');
    }
  }

  /// Cloud có nhóm dữ liệu thì tải về; cloud chưa có thì đẩy dữ liệu local lên.
  static Future<void> syncAll() async {
    final cloud = await _getCloud();
    final prefs = await SharedPreferences.getInstance();

    for (final entry in _keys.entries) {
      if (cloud.containsKey(entry.key)) {
        await prefs.setString(entry.value, jsonEncode(cloud[entry.key]));
      } else {
        final raw = prefs.getString(entry.value);
        if (raw != null) {
          await _putCloud(entry.key, jsonDecode(raw));
        }
      }
    }
  }
}
