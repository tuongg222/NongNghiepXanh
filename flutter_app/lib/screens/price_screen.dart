import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PriceScreen extends StatefulWidget {
  const PriceScreen({super.key});

  @override
  State<PriceScreen> createState() => _PriceScreenState();
}

class _PriceScreenState extends State<PriceScreen> {
  List<Map<String, dynamic>> prices = [];
  final crop = TextEditingController();
  final buy = TextEditingController();
  final sell = TextEditingController();
  String region = 'Cần Thơ';

  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString('nx_prices');
    if (raw != null) {
      prices = List<Map<String, dynamic>>.from(
        jsonDecode(raw).map((e) => Map<String, dynamic>.from(e)),
      );
    }
    if (mounted) setState(() {});
  }

  Future<void> save() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('nx_prices', jsonEncode(prices));
  }

  Future<void> addPrice() async {
    crop.clear();
    buy.clear();
    sell.clear();

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, refresh) => AlertDialog(
          title: const Text('🌾 Thêm giá nông sản'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: crop,
                  decoration: const InputDecoration(
                    labelText: 'Tên nông sản',
                    hintText: 'Ví dụ: Lúa OM18',
                  ),
                ),
                DropdownButtonFormField<String>(
                  value: region,
                  decoration: const InputDecoration(labelText: 'Khu vực'),
                  items: ['Cần Thơ', 'An Giang', 'Địa phương khác']
                      .map((e) => DropdownMenuItem(
                        value: e, child: Text(e),
                      )).toList(),
                  onChanged: (v) => refresh(() => region = v!),
                ),
                TextField(
                  controller: buy,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Giá mua (đồng/kg)',
                  ),
                ),
                TextField(
                  controller: sell,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Giá bán (đồng/kg)',
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

    final b = double.tryParse(buy.text);
    final s = double.tryParse(sell.text);

    if (ok != true || crop.text.trim().isEmpty ||
        b == null || s == null || b < 0 || s < 0) return;

    prices.insert(0, {
      'crop': crop.text.trim(),
      'region': region,
      'buy': b,
      'sell': s,
      'date': DateTime.now().toIso8601String(),
    });

    await save();
    if (mounted) setState(() {});
  }

  Future<void> deletePrice(int i) async {
    prices.removeAt(i);
    await save();
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📈 Giá nông sản'),
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
                  Text('💰 Theo dõi thị trường',
                    style: TextStyle(color: Colors.white,
                      fontSize: 23, fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Text('Quản lý giá mua và giá bán nông sản',
                    style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 12),
            const Card(
              child: Padding(
                padding: EdgeInsets.all(12),
                child: Text(
                  'ℹ️ Giá bên dưới do bạn nhập, không phải giá thị trường trực tiếp.',
                ),
              ),
            ),
            // THONG KE
            Card(
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(18),
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Row(
                  children: [
                    Expanded(
                      child: Column(
                        children: [
                          const Icon(Icons.inventory_2,
                              color: Colors.green, size: 28),
                          const SizedBox(height: 6),
                          Text('\${prices.length}',
                              style: const TextStyle(
                                  fontSize: 24,
                                  fontWeight: FontWeight.bold)),
                          const Text('Mặt hàng'),
                        ],
                      ),
                    ),
                    Expanded(
                      child: Column(
                        children: [
                          const Icon(Icons.show_chart,
                              color: Colors.blue, size: 28),
                          const SizedBox(height: 6),
                          Text(
                            prices.isEmpty
                                ? '0'
                                : (prices.fold<double>(
                                    0,
                                    (sum, e) =>
                                        sum + (e['sell'] as num).toDouble()
                                        - (e['buy'] as num).toDouble(),
                                  ) / prices.length).toStringAsFixed(0),
                            style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold),
                          ),
                          const Text('TB chênh lệch/kg'),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // BIEU DO
            if (prices.isNotEmpty) ...[
              const SizedBox(height: 10),
              Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('📊 So sánh giá mua / bán',
                          style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold)),
                      const SizedBox(height: 16),
                      SizedBox(
                        height: 220,
                        child: PriceChart(prices: prices),
                      ),
                      const SizedBox(height: 8),
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.circle, color: Colors.blue, size: 10),
                          SizedBox(width: 5),
                          Text('Giá mua'),
                          SizedBox(width: 18),
                          Icon(Icons.circle, color: Colors.green, size: 10),
                          SizedBox(width: 5),
                          Text('Giá bán'),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ],

            FilledButton.icon(
              onPressed: addPrice,
              icon: const Icon(Icons.add),
              label: const Text('Thêm giá nông sản'),
              style: FilledButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                padding: const EdgeInsets.all(15),
              ),
            ),
            const SizedBox(height: 12),
            if (prices.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('Chưa có dữ liệu giá 🌱')),
                ),
              ),
            ...prices.asMap().entries.map((e) {
              final i = e.key;
              final item = e.value;
              final profit = (item['sell'] as num) -
                  (item['buy'] as num);
              final d = DateTime.parse(item['date']);
              return Card(
                margin: const EdgeInsets.symmetric(vertical: 7),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(18),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(15),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Text('🌾', style: TextStyle(fontSize: 26)),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(item['crop'],
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold)),
                          ),
                          IconButton(
                            onPressed: () => deletePrice(i),
                            icon: const Icon(Icons.delete_outline,
                              color: Colors.red),
                          ),
                        ],
                      ),
                      Text('📍 ${item['region']}'),
                      Text('Giá mua: ${(item['buy'] as num).toStringAsFixed(0)} đ/kg'),
                      Text('Giá bán: ${(item['sell'] as num).toStringAsFixed(0)} đ/kg'),
                      const SizedBox(height: 6),
                      Text(
                        'Chênh lệch: ${profit.toStringAsFixed(0)} đ/kg',
                        style: TextStyle(
                          color: profit >= 0 ? Colors.green : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text('Cập nhật: ${d.day}/${d.month}/${d.year}',
                        style: const TextStyle(color: Colors.grey)),
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


class PriceChart extends StatelessWidget {
  final List<Map<String, dynamic>> prices;
  const PriceChart({super.key, required this.prices});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: _PricePainter(prices),
      child: const SizedBox.expand(),
    );
  }
}

class _PricePainter extends CustomPainter {
  final List<Map<String, dynamic>> prices;
  _PricePainter(this.prices);

  @override
  void paint(Canvas canvas, Size size) {
    if (prices.isEmpty) return;

    final values = prices.take(8).toList().reversed.toList();
    final maxValue = values.fold<double>(
      1,
      (m, e) => [
        m,
        (e['buy'] as num).toDouble(),
        (e['sell'] as num).toDouble(),
      ].reduce((a, b) => a > b ? a : b),
    );

    final grid = Paint()
      ..color = Colors.grey.withAlpha(45)
      ..strokeWidth = 1;

    for (int i = 0; i < 5; i++) {
      final y = size.height * i / 4;
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }

    final buyPaint = Paint()
      ..color = Colors.blue
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final sellPaint = Paint()
      ..color = Colors.green
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final buyPath = Path();
    final sellPath = Path();

    for (int i = 0; i < values.length; i++) {
      final x = values.length == 1
          ? size.width / 2
          : size.width * i / (values.length - 1);

      final b = (values[i]['buy'] as num).toDouble();
      final s = (values[i]['sell'] as num).toDouble();

      final yBuy = size.height - (b / maxValue * size.height);
      final ySell = size.height - (s / maxValue * size.height);

      if (i == 0) {
        buyPath.moveTo(x, yBuy);
        sellPath.moveTo(x, ySell);
      } else {
        buyPath.lineTo(x, yBuy);
        sellPath.lineTo(x, ySell);
      }

      canvas.drawCircle(Offset(x, yBuy), 4,
          Paint()..color = Colors.blue);
      canvas.drawCircle(Offset(x, ySell), 4,
          Paint()..color = Colors.green);
    }

    canvas.drawPath(buyPath, buyPaint);
    canvas.drawPath(sellPath, sellPaint);
  }

  @override
  bool shouldRepaint(covariant _PricePainter oldDelegate) => true;
}
