import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'api_service.dart';

class AuthService {
  static const _storage = FlutterSecureStorage();
  static const _tokenKey = 'auth_token';

  static String? token;
  static Map<String, dynamic>? user;

  static Future<void> restoreSession() async {
    token = await _storage.read(key: _tokenKey);
    if (token == null) return;

    try {
      final data = await me();
      user = data['user'];
    } catch (_) {
      await logout();
    }
  }

  static Future<Map<String, dynamic>> _post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    final response = await http.post(
      Uri.parse('${ApiService.workerBase}$endpoint'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(body),
    ).timeout(const Duration(seconds: 30));

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(data['error'] ?? 'HTTP ${response.statusCode}');
    }
    return data;
  }

  static Future<void> register(String username, String password) async {
    await _post('/auth/register', {
      'username': username,
      'password': password,
    });
  }

  static Future<Map<String, dynamic>> login(
    String username,
    String password,
  ) async {
    final data = await _post('/auth/login', {
      'username': username,
      'password': password,
    });

    token = data['token'] as String?;
    user = data['user'] as Map<String, dynamic>?;

    if (token == null) throw Exception('Worker không trả token');

    await _storage.write(key: _tokenKey, value: token);
    return data;
  }

  static Future<Map<String, dynamic>> me() async {
    if (token == null) throw Exception('Chưa đăng nhập');

    final response = await http.post(
      Uri.parse('${ApiService.workerBase}/auth/me'),
      headers: {'Authorization': 'Bearer $token'},
    ).timeout(const Duration(seconds: 30));

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode != 200) {
      throw Exception(data['error'] ?? 'Phiên đăng nhập hết hạn');
    }

    user = data['user'] as Map<String, dynamic>?;
    return data;
  }

  static Future<void> logout() async {
    try {
      if (token != null) {
        await http.post(
          Uri.parse('${ApiService.workerBase}/auth/logout'),
          headers: {'Authorization': 'Bearer $token'},
        );
      }
    } finally {
      token = null;
      user = null;
      await _storage.delete(key: _tokenKey);
    }
  }
}
