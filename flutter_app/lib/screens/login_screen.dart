import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import 'home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final username = TextEditingController();
  final password = TextEditingController();

  bool registering = false;
  bool busy = false;
  bool hidePassword = true;
  String? error;

  Future<void> submit() async {
    final u = username.text.trim();
    final p = password.text;

    if (u.isEmpty || p.isEmpty) {
      setState(() => error = 'Vui lòng nhập đầy đủ thông tin');
      return;
    }

    setState(() {
      busy = true;
      error = null;
    });

    try {
      if (registering) {
        await AuthService.register(u, p);
        if (!mounted) return;

        setState(() => registering = false);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Đăng ký thành công! Hãy đăng nhập.')),
        );
      } else {
        await AuthService.login(u, p);
        if (!mounted) return;

        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => error = e.toString().replaceFirst('Exception: ', ''));
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  void dispose() {
    username.dispose();
    password.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    const green = Color(0xFF167A45);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.eco, size: 76, color: green),
                  const SizedBox(height: 12),
                  const Text(
                    'Nông Nghiệp Xanh',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 27, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    registering ? 'Tạo tài khoản mới' : 'Chào mừng nhà nông trở lại!',
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 32),
                  TextField(
                    controller: username,
                    enabled: !busy,
                    autocorrect: false,
                    textCapitalization: TextCapitalization.none,
                    decoration: const InputDecoration(
                      labelText: 'Tên tài khoản',
                      prefixIcon: Icon(Icons.person_outline),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: password,
                    enabled: !busy,
                    obscureText: hidePassword,
                    decoration: InputDecoration(
                      labelText: 'Mật khẩu',
                      prefixIcon: const Icon(Icons.lock_outline),
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        onPressed: () => setState(() => hidePassword = !hidePassword),
                        icon: Icon(hidePassword ? Icons.visibility : Icons.visibility_off),
                      ),
                    ),
                  ),
                  if (registering) ...[
                    const SizedBox(height: 8),
                    const Text(
                      'Tên tài khoản 3–24 ký tự. Mật khẩu 10–128 ký tự.',
                      style: TextStyle(color: Colors.grey, fontSize: 12),
                    ),
                  ],
                  if (error != null) ...[
                    const SizedBox(height: 16),
                    Text(error!, style: const TextStyle(color: Colors.red)),
                  ],
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: busy ? null : submit,
                    style: FilledButton.styleFrom(
                      backgroundColor: green,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: busy
                        ? const SizedBox(
                            height: 22,
                            width: 22,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          )
                        : Text(registering ? 'ĐĂNG KÝ' : 'ĐĂNG NHẬP'),
                  ),
                  TextButton(
                    onPressed: busy
                        ? null
                        : () => setState(() {
                              registering = !registering;
                              error = null;
                            }),
                    child: Text(
                      registering
                          ? 'Đã có tài khoản? Đăng nhập'
                          : 'Chưa có tài khoản? Đăng ký',
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
