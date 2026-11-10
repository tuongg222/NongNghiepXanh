import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/sync_service.dart';

class FinanceScreen extends StatefulWidget {
  const FinanceScreen({super.key});

  @override
  State<FinanceScreen> createState() => _FinanceScreenState();
}

class _FinanceScreenState extends State<FinanceScreen> {
  List<Map<String, dynamic>> records = [];
  final title = TextEditingController();
  final money = TextEditingController();
  String type = 'Chi phí';
  String category = 'Phân bón';

  final categories = [
    'Giống', 'Phân bón', 'Thuốc bảo vệ cây',
    'Nhân công', 'Máy móc', 'Khác'
  ];

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final p = await SharedPreferences.getInstance();
    final raw = p.getString('nx_finance');
    if (raw != null) {
      records = List<Map<String, dynamic>>.from(
        jsonDecode(raw).map((e) => Map<String, dynamic>.from(e)),
      );
    }
    if (mounted) setState(() {});
  }

  Future<void> save() async {
    final p = await SharedPreferences.getInstance();
    await p.setString('nx_finance', jsonEncode(records));
    await SyncService.uploadKey('finance', records);
  }

  double get expenses => records
      .where((e) => e['type'] == 'Chi phí')
      .fold(0, (s, e) => s + (e['money'] as num).toDouble());

  double get revenue => records
      .where((e) => e['type'] == 'Doanh thu')
      .fold(0, (s, e) => s + (e['money'] as num).toDouble());

  Future<void> addRecord() async {
    title.clear();
    money.clear();
    type = 'Chi phí';
    category = categories.first;

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, refresh) => AlertDialog(
          title: const Text('💰 Thêm giao dịch'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: type,
                  decoration: const InputDecoration(labelText: 'Loại'),
                  items: ['Chi phí', 'Doanh thu'].map((e) =>
                    DropdownMenuItem(value: e, child: Text(e))).toList(),
                  onChanged: (v) => refresh(() {
                    type = v!;
                  }),
                ),
                if (type == 'Chi phí')
                  DropdownButtonFormField<String>(
                    value: category,
                    decoration: const InputDecoration(labelText: 'Danh mục'),
                    items: categories.map((e) =>
                      DropdownMenuItem(value: e, child: Text(e))).toList(),
                    onChanged: (v) => refresh(() => category = v!),
                  ),
                TextField(
                  controller: title,
                  decoration: const InputDecoration(
                    labelText: 'Tên giao dịch',
                    hintText: 'Ví dụ: Mua 10 bao phân',
                  ),
                ),
                TextField(
                  controller: money,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Số tiền (VNĐ)',
                  ),
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

    final amount = double.tryParse(money.text);
    if (ok != true || title.text.trim().isEmpty ||
        amount == null || amount < 0) return;

    records.insert(0, {
      'type': type,
      'category': type == 'Chi phí' ? category : 'Thu hoạch',
      'title': title.text.trim(),
      'money': amount,
      'date': DateTime.now().toIso8601String(),
    });

    await save();
    if (mounted) setState(() {});
  }

  Future<void> removeRecord(int i) async {
    records.removeAt(i);
    await save();
    if (mounted) setState(() {});
  }

  String fmt(double n) =>
      n.toStringAsFixed(0).replaceAllMapped(
        RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'),
        (m) => '${m[1]}.',
      );

  @override
  Widget build(BuildContext context) {
    final profit = revenue - expenses;

    return Scaffold(
      appBar: AppBar(
        title: const Text('💰 Chi phí & lợi nhuận'),
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
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.green.shade700, Colors.teal.shade400],
                ),
                borderRadius: BorderRadius.circular(22),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('📊 Tổng kết tài chính',
                    style: TextStyle(color: Colors.white,
                      fontSize: 23, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Text('Lợi nhuận: ${fmt(profit)} VNĐ',
                    style: const TextStyle(color: Colors.white,
                      fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 6),
                  Text('Trạng thái: ${profit >= 0 ? "Có lãi" : "Đang lỗ"}',
                    style: const TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(children: [
                      const Icon(Icons.arrow_downward, color: Colors.red),
                      const Text('Chi phí'),
                      Text('${fmt(expenses)} đ',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    ]),
                  ),
                )),
                Expanded(child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(children: [
                      const Icon(Icons.arrow_upward, color: Colors.green),
                      const Text('Doanh thu'),
                      Text('${fmt(revenue)} đ',
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                    ]),
                  ),
                )),
              ],
            ),
            FilledButton.icon(
              onPressed: addRecord,
              icon: const Icon(Icons.add),
              label: const Text('Thêm giao dịch'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                padding: const EdgeInsets.all(15),
              ),
            ),
            const SizedBox(height: 12),
            if (records.isEmpty)
              const Card(child: Padding(
                padding: EdgeInsets.all(24),
                child: Center(child: Text('Chưa có giao dịch')),
              )),
            ...records.asMap().entries.map((e) {
              final i = e.key;
              final r = e.value;
              final isCost = r['type'] == 'Chi phí';
              final d = DateTime.parse(r['date']);
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 6),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: isCost
                        ? Colors.red.shade50 : Colors.green.shade50,
                    child: Icon(
                      isCost ? Icons.shopping_cart : Icons.agriculture,
                      color: isCost ? Colors.red : Colors.green,
                    ),
                  ),
                  title: Text(r['title'],
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    '${r['category']} • ${d.day}/${d.month}/${d.year}',
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('${isCost ? "-" : "+"}${fmt((r['money'] as num).toDouble())}đ',
                        style: TextStyle(
                          color: isCost ? Colors.red : Colors.green,
                          fontWeight: FontWeight.bold,
                        )),
                      IconButton(
                        icon: const Icon(Icons.delete_outline),
                        onPressed: () => removeRecord(i),
                      ),
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
