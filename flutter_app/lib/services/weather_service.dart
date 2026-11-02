import 'dart:convert';
import 'package:http/http.dart' as http;

class WeatherService {
  // Mặc định khu vực Cần Thơ; sau này thay bằng GPS người dùng.
  static Future<Map<String, dynamic>> current({
    double latitude = 10.03,
    double longitude = 105.78,
  }) async {
    final uri = Uri.https('api.open-meteo.com', '/v1/forecast', {
      'latitude': '$latitude',
      'longitude': '$longitude',
      'current': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
      'timezone': 'Asia/Ho_Chi_Minh',
    });
    final res = await http.get(uri).timeout(const Duration(seconds: 20));
    if (res.statusCode != 200) throw Exception('Không tải được thời tiết');
    return jsonDecode(res.body) as Map<String, dynamic>;
  }
}
