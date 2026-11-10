import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/sync_service.dart';

class SeasonScreen extends StatefulWidget {
  const SeasonScreen({super.key});

  @override
  State<SeasonScreen> createState() => _SeasonScreenState();
}

class _SeasonScreenState extends State<SeasonScreen> {
  List<Map<String, dynamic>> seasons = [];
  final name = TextEditingController();
  final area = TextEditingController();
  DateTime planting = DateTime.now();
  DateTime harvest = DateTime.now().add(const Duration(days: 100));

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('nx_seasons');
    if (raw != null) {
      seasons = List<Map<String, dynamic>>.from(
        jsonDecode(raw).map((e) => Map<String, dynamic>.from(e)),
      );
    }
    if (mounted) setState(() {});
  }

  Future<void> save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('nx_seasons', jsonEncode(seasons));
    await SyncService.uploadKey('seasons', seasons);
  }

  Future<void> addSeason() async {
    name.clear();
    area.clear();

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, refresh) => AlertDialog(
          title: const Text('🌱 Thêm mùa vụ'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: name,
                  decoration: const InputDecoration(
                    labelText: 'Tên cây trồng',
                    hintText: 'Ví dụ: Lúa OM18',
                  ),
                ),
                TextField(
                  controller: area,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Diện tích (m²)',
                  ),
                ),
                const SizedBox(height: 12),
                TextButton(
                  onPressed: () async {
                    final d = await showDatePicker(
                      context: ctx,
                      initialDate: planting,
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2100),
                    );
                    if (d != null) refresh(() => planting = d);
                  },
                  child: Text('Ngày gieo: ${planting.day}/${planting.month}/${planting.year}'),
                ),
                TextButton(
                  onPressed: () async {
                    final d = await showDatePicker(
                      context: ctx,
                      initialDate: harvest,
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2100),
                    );
                    if (d != null) refresh(() => harvest = d);
                  },
                  child: Text('Thu hoạch: ${harvest.day}/${harvest.month}/${harvest.year}'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Hủy'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Lưu'),
            ),
          ],
        ),
      ),
    );

    if (result != true || name.text.trim().isEmpty) return;

    seasons.add({
      'name': name.text.trim(),
      'area': double.tryParse(area.text) ?? 0,
      'planting': planting.toIso8601String(),
      'harvest': harvest.toIso8601String(),
    });

    await save();
    if (mounted) setState(() {});
  }

  Future<void> removeSeason(int i) async {
    seasons.removeAt(i);
    await save();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🌾 Quản lý mùa vụ'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.green.shade50, Colors.white],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.green.shade700, Colors.teal.shade400],
                ),
                borderRadius: BorderRadius.circular(22),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('🌿 Nhật ký mùa vụ',
                    style: TextStyle(color: Colors.white, fontSize: 23,
                      fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Theo dõi cây trồng và lịch thu hoạch',
                    style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: addSeason,
              icon: const Icon(Icons.add),
              label: const Text('Thêm mùa vụ'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                padding: const EdgeInsets.all(15),
              ),
            ),
            const SizedBox(height: 12),
            if (seasons.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(
                    child: Text('Chưa có mùa vụ. Hãy thêm mùa vụ đầu tiên 🌱'),
                  ),
                ),
              ),
            ...seasons.asMap().entries.map((entry) {
              final i = entry.key;
              final s = entry.value;
              final start = DateTime.parse(s['planting']);
              final end = DateTime.parse(s['harvest']);
              final total = end.difference(start).inDays;
              final passed = DateTime.now().difference(start).inDays;
              final progress = total <= 0 ? 0.0 :
                  (passed / total).clamp(0.0, 1.0);

              return Card(
                elevation: 3,
                margin: const EdgeInsets.symmetric(vertical: 8),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text('🌾', style: TextStyle(fontSize: 28)),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(s['name'],
                              style: const TextStyle(fontSize: 18,
                                fontWeight: FontWeight.bold)),
                          ),
                          IconButton(
                            onPressed: () => removeSeason(i),
                            icon: const Icon(Icons.delete_outline,
                              color: Colors.red),
                          ),
                        ],
                      ),
                      Text('Diện tích: ${s['area']} m²'),
                      Text('Gieo: ${start.day}/${start.month}/${start.year}'),
                      Text('Thu hoạch: ${end.day}/${end.month}/${end.year}'),
                      const SizedBox(height: 12),
                      LinearProgressIndicator(
                        value: progress,
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(10),
                        color: Colors.green,
                      ),
                      const SizedBox(height: 6),
                      Text('Tiến độ thời gian: ${(progress * 100).round()}%'),
                    ],
                  ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
