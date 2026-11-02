import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const NongNghiepXanhApp());
}

class NongNghiepXanhApp extends StatelessWidget {
  const NongNghiepXanhApp({super.key});

  @override
  Widget build(BuildContext context) {
    const green = Color(0xFF167A45);
    return MaterialApp(
      title: 'Nông Nghiệp Xanh',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: green),
        scaffoldBackgroundColor: const Color(0xFFF5F8F4),
        appBarTheme: const AppBarTheme(
          backgroundColor: Color(0xFFF5F8F4),
          foregroundColor: Color(0xFF163D27),
        ),
      ),
      home: const HomeScreen(),
    );
  }
}
