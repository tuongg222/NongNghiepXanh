import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/weather_service.dart';
import 'diagnose_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? weather;
  String backendStatus = 'Đang kiểm tra kết nối…';
  bool loading = true;

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    setState(() => loading = true);
    try {
      final results = await Future.wait([WeatherService.current(), ApiService.health()]);
      weather = results[0];
      final health = results[1];
      backendStatus = 'Backend hoạt động • AI: ${health['aiConnected'] == true ? 'sẵn sàng' : 'chưa kết nối'}';
    } catch (e) {
      backendStatus = 'Chưa kết nối được máy chủ';
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final current = weather?['current'] as Map<String, dynamic>?;
    return Scaffold(
      appBar: AppBar(
        title: const Row(children: [
          Icon(Icons.eco, color: Color(0xFF167A45)),
          SizedBox(width: 8),
          Text('Nông Nghiệp Xanh', style: TextStyle(fontWeight: FontWeight.w800)),
        ]),
        actions: [IconButton(onPressed: refresh, icon: const Icon(Icons.refresh))],
      ),
      body: RefreshIndicator(
        onRefresh: refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: [Color(0xFF167A45), Color(0xFF39A96B)]),
                borderRadius: BorderRadius.circular(24),
              ),
              child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('Xin chào nhà nông 👋', style: TextStyle(color: Colors.white70)),
                SizedBox(height: 8),
                Text('Chăm cây thông minh\nMùa vụ bội thu', style: TextStyle(color: Colors.white, fontSize: 25, fontWeight: FontWeight.bold)),
                SizedBox(height: 12),
                Text('AI • Thời tiết • Nhật ký mùa vụ', style: TextStyle(color: Colors.white)),
              ]),
            ),
            const SizedBox(height: 16),
            _sectionTitle('Thời tiết hiện tại'),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(18),
                child: loading ? const Center(child: CircularProgressIndicator()) :
                current == null ? const Text('Chưa có dữ liệu thời tiết') :
                Row(children: [
                  const Icon(Icons.wb_sunny_outlined, size: 48, color: Colors.orange),
                  const SizedBox(width: 16),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    Text('${current['temperature_2m']}°C', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold)),
                    Text('Độ ẩm ${current['relative_humidity_2m']}%'),
                    Text('Gió ${current['wind_speed_10m']} km/h'),
                  ])),
                ]),
              ),
            ),
            const SizedBox(height: 16),
            _sectionTitle('Công cụ nông nghiệp'),
            _feature(Icons.document_scanner_outlined, 'AI chẩn đoán cây trồng', 'Chụp ảnh lá và nhận tư vấn', () {
              Navigator.push(context, MaterialPageRoute(builder: (_) => const DiagnoseScreen()));
            }),
            _feature(Icons.cloud_outlined, 'Dự báo thời tiết', 'Theo dõi điều kiện canh tác', refresh),
            _feature(Icons.grass, 'Quản lý mùa vụ', 'Theo dõi tiến trình cây trồng', () => _comingSoon(context)),
            _feature(Icons.menu_book_outlined, 'Nhật ký nông nghiệp', 'Lưu hoạt động và ghi chú', () => _comingSoon(context)),
            const SizedBox(height: 10),
            Text(backendStatus, textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) => Padding(
    padding: const EdgeInsets.only(bottom: 8),
    child: Text(text, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
  );

  Widget _feature(IconData icon, String title, String subtitle, VoidCallback action) => Card(
    margin: const EdgeInsets.only(bottom: 10),
    child: ListTile(
      leading: CircleAvatar(backgroundColor: const Color(0xFFE1F3E7), child: Icon(icon, color: const Color(0xFF167A45))),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(subtitle),
      trailing: const Icon(Icons.chevron_right),
      onTap: action,
    ),
  );

  void _comingSoon(BuildContext context) => ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('Tính năng sẽ được kết nối ở bước tiếp theo')),
  );
}
