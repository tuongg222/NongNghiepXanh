import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/sync_service.dart';

class FieldScreen extends StatefulWidget {
  const FieldScreen({super.key});

  @override
  State<FieldScreen> createState() => _FieldScreenState();
}

class _FieldScreenState extends State<FieldScreen> {
  List<Map<String, dynamic>> fields = [];
  final name = TextEditingController();
  final area = TextEditingController();
  final crop = TextEditingController();
  final variety = TextEditingController();
  String unit = 'm²';
  DateTime planting = DateTime.now();
  DateTime harvest = DateTime.now().add(const Duration(days: 100));

  @override
  void initState() {
    super.initState();
    load();
  }

  @override
  void dispose() {
    name.dispose();
    area.dispose();
    crop.dispose();
    variety.dispose();
    super.dispose();
  }

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('nx_fields');
    if (raw != null) {
      fields = List<Map<String, dynamic>>.from(
        jsonDecode(raw).map((e) => Map<String, dynamic>.from(e)),
      );
    }
    if (mounted) setState(() {});
  }

  Future<void> save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('nx_fields', jsonEncode(fields));
    await SyncService.uploadKey('fields', fields);
  }

  String dateText(DateTime d) => '${d.day}/${d.month}/${d.year}';

  Future<void> chooseDate(bool isPlanting, StateSetter refresh) async {
    final current = isPlanting ? planting : harvest;
    final d = await showDatePicker(
      context: context,
      initialDate: current,
      firstDate: DateTime(2020),
      lastDate: DateTime(2100),
    );
    if (d != null) {
      refresh(() {
        if (isPlanting) {
          planting = d;
        } else {
          harvest = d;
        }
      });
    }
  }

  Future<void> editField({int? index}) async {
    final editing = index != null;
    final old = editing ? fields[index] : <String, dynamic>{};

    name.text = old['name']?.toString() ?? '';
    area.text = old['area']?.toString() ?? '';
    crop.text = old['crop']?.toString() ?? '';
    variety.text = old['variety']?.toString() ?? '';
    unit = old['unit']?.toString() ?? 'm²';
    planting = DateTime.tryParse(old['planting']?.toString() ?? '') ?? DateTime.now();
    harvest = DateTime.tryParse(old['harvest']?.toString() ?? '') ??
        DateTime.now().add(const Duration(days: 100));

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, refresh) => AlertDialog(
          title: Text(editing ? '✏️ Sửa thửa ruộng' : '🌱 Thêm thửa ruộng'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: name,
                  decoration: const InputDecoration(labelText: 'Tên thửa ruộng'),
                ),
                TextField(
                  controller: area,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Diện tích'),
                ),
                DropdownButtonFormField<String>(
                  value: unit,
                  decoration: const InputDecoration(labelText: 'Đơn vị'),
                  items: const [
                    DropdownMenuItem(value: 'm²', child: Text('Mét vuông (m²)')),
                    DropdownMenuItem(value: 'ha', child: Text('Hecta (ha)')),
                  ],
                  onChanged: (v) => refresh(() => unit = v ?? 'm²'),
                ),
                TextField(
                  controller: crop,
                  decoration: const InputDecoration(labelText: 'Cây trồng'),
                ),
                TextField(
                  controller: variety,
                  decoration: const InputDecoration(labelText: 'Giống cây'),
                ),
                const SizedBox(height: 8),
                TextButton(
                  onPressed: () => chooseDate(true, refresh),
                  child: Text('Ngày gieo: ${dateText(planting)}'),
                ),
                TextButton(
                  onPressed: () => chooseDate(false, refresh),
                  child: Text('Ngày thu hoạch: ${dateText(harvest)}'),
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

    final item = <String, dynamic>{
      'name': name.text.trim(),
      'area': double.tryParse(area.text) ?? 0,
      'unit': unit,
      'crop': crop.text.trim(),
      'variety': variety.text.trim(),
      'planting': planting.toIso8601String(),
      'harvest': harvest.toIso8601String(),
    };

    if (editing) {
      fields[index] = item;
    } else {
      fields.add(item);
    }

    await save();
    if (mounted) setState(() {});
  }

  Future<void> removeField(int index) async {
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xóa thửa ruộng?'),
        content: Text('Bạn muốn xóa "${fields[index]['name']}" không?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Hủy'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Xóa'),
          ),
        ],
      ),
    );

    if (ok != true) return;
    fields.removeAt(index);
    await save();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final total = fields.fold<double>(
      0,
      (sum, f) => sum + ((f['area'] as num?)?.toDouble() ?? 0),
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('🌾 Thửa ruộng'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => editField(),
        icon: const Icon(Icons.add),
        label: const Text('Thêm ruộng'),
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
            Card(
              color: Colors.green.shade700,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('🌿 Tổng quan nông trại',
                        style: TextStyle(color: Colors.white, fontSize: 20,
                            fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    Text('${fields.length} thửa ruộng',
                        style: const TextStyle(color: Colors.white)),
                    Text('Tổng diện tích: ${total.toStringAsFixed(2)} (theo đơn vị từng ruộng)',
                        style: const TextStyle(color: Colors.white70)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 12),
            if (fields.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('Chưa có thửa ruộng. Hãy nhấn Thêm ruộng!')),
                ),
              ),
            ...fields.asMap().entries.map((entry) {
              final i = entry.key;
              final f = entry.value;
              final p = DateTime.tryParse(f['planting']?.toString() ?? '');
              final h = DateTime.tryParse(f['harvest']?.toString() ?? '');
              return Card(
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.green.shade100,
                    child: const Icon(Icons.grass, color: Colors.green),
                  ),
                  title: Text(f['name']?.toString() ?? 'Thửa ruộng',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    '🌱 ${f['crop'] ?? 'Chưa ghi cây'} • ${f['variety'] ?? 'Chưa ghi giống'}\n'
                    '📐 ${f['area'] ?? 0} ${f['unit'] ?? 'm²'}\n'
                    '📅 Gieo: ${p == null ? '--' : dateText(p)} • Thu: ${h == null ? '--' : dateText(h)}',
                  ),
                  isThreeLine: true,
                  trailing: PopupMenuButton<String>(
                    onSelected: (v) {
                      if (v == 'edit') editField(index: i);
                      if (v == 'delete') removeField(i);
                    },
                    itemBuilder: (_) => const [
                      PopupMenuItem(value: 'edit', child: Text('✏️ Sửa')),
                      PopupMenuItem(value: 'delete', child: Text('🗑️ Xóa')),
                    ],
                  ),
                ),
              );
            }),
            const SizedBox(height: 80),
          ],
        ),
      ),
    );
  }
}
