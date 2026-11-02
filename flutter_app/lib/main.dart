import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'services/auth_service.dart';

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
      home: const AuthGate(),
    );
  }
}

class AuthGate extends StatefulWidget {
  const AuthGate({super.key});

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  late final Future<void> session = AuthService.restoreSession();

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<void>(
      future: session,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        return AuthService.token != null
            ? const HomeScreen()
            : const LoginScreen();
      },
    );
  }
}
