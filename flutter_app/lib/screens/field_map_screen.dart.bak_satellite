import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:geolocator/geolocator.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';

class FieldMapScreen extends StatefulWidget {
  const FieldMapScreen({super.key});

  @override
  State<FieldMapScreen> createState() => _FieldMapScreenState();
}

class _FieldMapScreenState extends State<FieldMapScreen> {
  final mapController = MapController();
  final points = <LatLng>[];
  bool locating = false;
  String fieldName = 'Ruộng của tôi';

  static const distance = Distance();

  double get area {
    if (points.length < 3) return 0;

    final origin = points.first;
    final xy = points.map((p) {
      final x = (p.longitude - origin.longitude) *
          111320 *
          math.cos(origin.latitude * math.pi / 180);
      final y = (p.latitude - origin.latitude) * 110574;
      return [x, y];
    }).toList();

    double sum = 0;
    for (int i = 0; i < xy.length; i++) {
      final j = (i + 1) % xy.length;
      sum += xy[i][0] * xy[j][1] - xy[j][0] * xy[i][1];
    }
    return sum.abs() / 2;
  }

  String fmt(double m) {
    if (m >= 1000) return '${(m / 1000).toStringAsFixed(3)} km';
    return '${m.toStringAsFixed(1)} m';
  }

  Future<void> locate() async {
    setState(() => locating = true);
    try {
      bool enabled = await Geolocator.isLocationServiceEnabled();
      if (!enabled) {
        throw Exception('Hãy bật GPS điện thoại');
      }

      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.denied ||
          permission == LocationPermission.deniedForever) {
        throw Exception('Ứng dụng chưa được cấp quyền GPS');
      }

      final p = await Geolocator.getCurrentPosition();
      final center = LatLng(p.latitude, p.longitude);
      mapController.move(center, 18);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'GPS: ${p.latitude.toStringAsFixed(6)}, '
              '${p.longitude.toStringAsFixed(6)}',
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString().replaceFirst('Exception: ', ''))),
        );
      }
    } finally {
      if (mounted) setState(() => locating = false);
    }
  }

  void addPoint(LatLng p) {
    setState(() => points.add(p));
  }

  void undo() {
    if (points.isEmpty) return;
    setState(() => points.removeLast());
  }

  void clearPoints() {
    setState(() => points.clear());
  }

  Future<void> saveField() async {
    if (points.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Cần ít nhất 3 điểm để đo diện tích')),
      );
      return;
    }

    final name = TextEditingController(text: fieldName);
    final ok = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Lưu thửa ruộng'),
        content: TextField(
          controller: name,
          decoration: const InputDecoration(labelText: 'Tên thửa'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Lưu'),
          ),
        ],
      ),
    );

    if (ok != true) return;

    fieldName = name.text.trim().isEmpty ? 'Ruộng của tôi' : name.text.trim();
    final prefs = await SharedPreferences.getInstance();
    final fields = prefs.getStringList('nx_fields') ?? [];
    fields.add(
      '$fieldName|${area.toStringAsFixed(2)}|'
      '${points.map((p) => '${p.latitude},${p.longitude}').join(';')}',
    );
    await prefs.setStringList('nx_fields', fields);

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Đã lưu thửa ruộng trên thiết bị')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final closed = points.length >= 3 ? [...points, points.first] : points;

    return Scaffold(
      appBar: AppBar(
        title: const Text('GPS đo đất'),
        actions: [
          IconButton(
            onPressed: undo,
            tooltip: 'Hoàn tác điểm',
            icon: const Icon(Icons.undo),
          ),
          IconButton(
            onPressed: clearPoints,
            tooltip: 'Xóa điểm',
            icon: const Icon(Icons.delete_outline),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: FlutterMap(
              mapController: mapController,
              options: MapOptions(
                initialCenter: const LatLng(10.03, 105.78),
                initialZoom: 14,
                onTap: (_, point) => addPoint(point),
              ),
              children: [
                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.nongnghiep.xanh',
                ),
                if (points.length >= 3)
                  PolygonLayer(
                    polygons: [
                      Polygon(
                        points: points,
                        color: Colors.green.withOpacity(.25),
                        borderColor: Colors.green,
                        borderStrokeWidth: 3,
                      ),
                    ],
                  ),
                PolylineLayer(
                  polylines: [
                    if (points.length >= 2)
                      Polyline(
                        points: closed,
                        color: Colors.green,
                        strokeWidth: 3,
                      ),
                  ],
                ),
                MarkerLayer(
                  markers: points.asMap().entries.map((entry) {
                    return Marker(
                      point: entry.value,
                      width: 35,
                      height: 35,
                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.green,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                        ),
                        child: Center(
                          child: Text(
                            '${entry.key + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
          ),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(18),
            decoration: const BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'DIỆN TÍCH THỬA ĐẤT',
                  style: TextStyle(
                    color: Colors.grey,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '${area.toStringAsFixed(2)} m²',
                  style: const TextStyle(
                    color: Color(0xFF167A45),
                    fontSize: 28,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                Text(
                  '${(area / 10000).toStringAsFixed(4)} ha'
                  ' • ${(area / 1000).toStringAsFixed(3)} công (1 công = 1.000 m²)',
                  style: const TextStyle(color: Colors.black54),
                ),
                const SizedBox(height: 12),
                if (points.length >= 2)
                  ...List.generate(points.length, (i) {
                    final j = (i + 1) % points.length;
                    final length = distance(points[i], points[j]);
                    return Padding(
                      padding: const EdgeInsets.symmetric(vertical: 2),
                      child: Text(
                        'Cạnh ${i + 1}: ${fmt(length)}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    );
                  }),
                const SizedBox(height: 12),
                const Text(
                  'Chạm bản đồ để thêm điểm ranh giới. '
                  'Cần tối thiểu 3 điểm để tính diện tích.',
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: locating ? null : locate,
                        icon: locating
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.my_location),
                        label: const Text('Định vị GPS'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: saveField,
                        icon: const Icon(Icons.save),
                        label: const Text('Lưu ruộng'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
