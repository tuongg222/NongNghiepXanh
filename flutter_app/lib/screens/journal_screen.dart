import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class JournalScreen extends StatefulWidget {
  const JournalScreen({super.key});

  @override
  State<JournalScreen> createState() => _JournalScreenState();
}

class _JournalScreenState extends State<JournalScreen> {
  List<Map<String, dynamic>> entries = [];
  final note = TextEditingController();
  final amount = TextEditingController();
  String type = 'Tưới nước';
  DateTime date = DateTime.now();

  final types = ['Tưới nước', 'Bón phân', 'Gieo trồng',
    'Phun thuốc', 'Thu hoạch', 'Công việc khác'];

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('nx_journal');
    if (raw != null) {
      entries = List<Map<String, dynamic>>.from(
        jsonDecode(raw).map((e) => Map<String, dynamic>.from(e)),
      );
    }
    if (mounted) setState(() {});
  }

  Future<void> save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('nx_journal', jsonEncode(entries));
  }

  Future<void> addEntry() async {
    note.clear();
    amount.clear();
    date = DateTime.now();
    type = types.first;

    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, refresh) => AlertDialog(
          title: const Text('📝 Ghi nhật ký'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  value: type,
                  decoration: const InputDecoration(labelText: 'Công việc'),
                  items: types.map((t) => DropdownMenuItem(
                    value: t, child: Text(t),
                  )).toList(),
                  onChanged: (v) => refresh(() => type = v!),
                ),
                TextField(
                  controller: amount,
                  decoration: const InputDecoration(
                    labelText: 'Lượng sử dụng (nếu có)',
                    hintText: 'Ví dụ: 20 kg, 500 lít',
                  ),
                ),
                TextField(
                  controller: note,
                  maxLines: 3,
                  decoration: const InputDecoration(
                    labelText: 'Ghi chú',
                    hintText: 'Mô tả công việc...',
                  ),
                ),
                TextButton(
                  onPressed: () async {
                    final d = await showDatePicker(
                      context: ctx,
                      initialDate: date,
                      firstDate: DateTime(2020),
                      lastDate: DateTime(2100),
                    );
                    if (d != null) refresh(() => date = d);
                  },
                  child: Text('Ngày: ${date.day}/${date.month}/${date.year}'),
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

    if (result != true) return;

    entries.insert(0, {
      'type': type,
      'amount': amount.text.trim(),
      'note': note.text.trim(),
      'date': date.toIso8601String(),
    });

    await save();
    if (mounted) setState(() {});
  }

  Future<void> deleteEntry(int i) async {
    entries.removeAt(i);
    await save();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📒 Nhật ký canh tác'),
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
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('🌿 Nhật ký nhà nông',
                    style: TextStyle(color: Colors.white,
                      fontSize: 23, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Lưu lại từng công việc trên ruộng',
                    style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: addEntry,
              icon: const Icon(Icons.add),
              label: const Text('Ghi công việc mới'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                padding: const EdgeInsets.all(15),
              ),
            ),
            const SizedBox(height: 12),
            if (entries.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(
                    child: Text('Chưa có nhật ký nào 🌱'),
                  ),
                ),
              ),
            ...entries.asMap().entries.map((e) {
              final i = e.key;
              final item = e.value;
              final d = DateTime.parse(item['date']);
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 7),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: Color(0xFFE0F2E5),
                    child: Icon(Icons.eco, color: Colors.green),
                  ),
                  title: Text(item['type'],
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text(
                    '${d.day}/${d.month}/${d.year}'
                    '${item['amount'].toString().isNotEmpty ? '\n${item['amount']}' : ''}'
                    '${item['note'].toString().isNotEmpty ? '\n${item['note']}' : ''}',
                  ),
                  isThreeLine: true,
                  trailing: IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    onPressed: () => deleteEntry(i),
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
