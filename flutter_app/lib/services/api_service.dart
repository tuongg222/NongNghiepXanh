import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String workerBase =
      'https://nongnghiep-xanh-ai.nguyenduytuong093.workers.dev';

  static Future<Map<String, dynamic>> health() async {
    final response = await http
        .get(Uri.parse('$workerBase/health'))
        .timeout(const Duration(seconds: 20));

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(data['error'] ?? 'Worker lỗi');
    }
    return data;
  }

  static Future<Map<String, dynamic>> diagnose({
    required String imageBase64,
    required String mimeType,
    String context = '',
  }) async {
    final response = await http.post(
      Uri.parse('$workerBase/diagnose'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'image': 'data:$mimeType;base64,$imageBase64',
        'context': context,
      }),
    ).timeout(const Duration(seconds: 120));

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception(data['error'] ?? 'AI lỗi HTTP ${response.statusCode}');
    }

    return data;
  }
}
