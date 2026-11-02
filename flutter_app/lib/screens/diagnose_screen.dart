import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class DiagnoseScreen extends StatefulWidget {
  const DiagnoseScreen({super.key});
  @override
  State<DiagnoseScreen> createState() => _DiagnoseScreenState();
}

class _DiagnoseScreenState extends State<DiagnoseScreen> {
  final picker = ImagePicker();
  File? image;
  bool busy = false;
  String? result;
  String? error;

  Future<void> chooseImage() async {
    final picked = await picker.pickImage(source: ImageSource.camera, imageQuality: 85);
    if (picked != null) setState(() { image = File(picked.path); result = null; error = null; });
  }

  Future<void> analyze() async {
    if (image == null) return;
    setState(() { busy = true; error = null; result = null; });
    try {
      final bytes = await image!.readAsBytes();
      final response = await ApiService.diagnose(
        imageBase64: base64Encode(bytes),
        mimeType: image!.path.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg',
      );
      result = const JsonEncoder.withIndent('  ').convert(response);
    } catch (e) {
      error = e.toString();
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('AI chẩn đoán cây trồng')),
    body: ListView(padding: const EdgeInsets.all(20), children: [
      const Text('Chụp ảnh lá hoặc bộ phận cây cần kiểm tra. Ảnh rõ nét giúp AI phân tích tốt hơn.'),
      const SizedBox(height: 16),
      OutlinedButton.icon(onPressed: chooseImage, icon: const Icon(Icons.camera_alt), label: const Text('Chụp ảnh cây')),
      if (image != null) ...[
        const SizedBox(height: 12),
        ClipRRect(borderRadius: BorderRadius.circular(16), child: Image.file(image!, height: 260, fit: BoxFit.cover)),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: busy ? null : analyze, icon: const Icon(Icons.auto_awesome), label: const Text('Phân tích bằng AI')),
      ],
      if (busy) const Padding(padding: EdgeInsets.all(24), child: Center(child: CircularProgressIndicator())),
      if (error != null) Card(color: Colors.red.shade50, child: Padding(padding: const EdgeInsets.all(12), child: Text(error!, style: TextStyle(color: Colors.red.shade800)))),
      if (result != null) Card(child: Padding(padding: const EdgeInsets.all(14), child: SelectableText(result!))),
    ]),
  );
}
