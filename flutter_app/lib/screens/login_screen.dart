import 'dart:ui';
import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../widgets/rice_cinematic.dart';
import 'home_screen.dart';

const green = Color(0xFF16A05A);
const darkGreen = Color(0xFF064E35);

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with TickerProviderStateMixin {
  final username = TextEditingController();
  final password = TextEditingController();

  late final AnimationController animationController;
  late final AnimationController riceController;
  late final AnimationController introController;
  late final Animation<double> introScale;
  late final Animation<double> formOpacity;
  late final Animation<Offset> formSlide;
  late final Animation<double> fade;
  late final Animation<Offset> slide;

  bool registering = false;
  bool busy = false;
  bool hidePassword = true;
  String? error;

  @override
  void initState() {
    super.initState();

    animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    );

    fade = CurvedAnimation(
      parent: animationController,
      curve: Curves.easeOut,
    );

    slide = Tween<Offset>(
      begin: const Offset(0, .15),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: animationController,
        curve: Curves.easeOutCubic,
      ),
    );

    animationController.forward();

    introController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3600),
    );

    introScale = Tween<double>(
      begin: 0.05,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: introController,
      curve: Curves.easeOutExpo,
    ));

    formOpacity = CurvedAnimation(
      parent: introController,
      curve: const Interval(.55, 1.0, curve: Curves.easeIn),
    );

    formSlide = Tween<Offset>(
      begin: const Offset(0, .16),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: introController,
      curve: const Interval(.55, 1.0, curve: Curves.easeOutCubic),
    ));

    introController.forward();

    riceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);
  }

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
          const SnackBar(
            content: Text('Đăng ký thành công! Hãy đăng nhập.'),
          ),
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
        setState(() {
          error = e.toString().replaceFirst('Exception: ', '');
        });
      }
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  void dispose() {
    animationController.dispose();
    riceController.dispose();
    introController.dispose();
    username.dispose();
    password.dispose();
    super.dispose();
  }

  Widget glass({
    required Widget child,
    double radius = 25,
  }) {
    return ClipRRect(
      borderRadius: BorderRadius.circular(radius),
      child: BackdropFilter(
        filter: ImageFilter.blur(sigmaX: 18, sigmaY: 18),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(.13),
            borderRadius: BorderRadius.circular(radius),
            border: Border.all(
              color: Colors.white.withOpacity(.25),
            ),
          ),
          child: child,
        ),
      ),
    );
  }

  Widget input({
    required TextEditingController controller,
    required String label,
    required IconData icon,
    bool passwordField = false,
  }) {
    return TextField(
      controller: controller,
      enabled: !busy,
      obscureText: passwordField && hidePassword,
      autocorrect: false,
      style: const TextStyle(color: Colors.white, fontSize: 15),
      decoration: InputDecoration(
        labelText: label,
        labelStyle: TextStyle(color: Colors.white.withOpacity(.7)),
        prefixIcon: Icon(icon, color: Colors.white70),
        suffixIcon: passwordField
            ? IconButton(
                onPressed: () {
                  setState(() => hidePassword = !hidePassword);
                },
                icon: Icon(
                  hidePassword
                      ? Icons.visibility_outlined
                      : Icons.visibility_off_outlined,
                  color: Colors.white70,
                ),
              )
            : null,
        filled: true,
        fillColor: Colors.white.withOpacity(.07),
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 19,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: BorderSide(color: Colors.white.withOpacity(.15)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: BorderSide(color: Colors.white.withOpacity(.18)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(18),
          borderSide: const BorderSide(color: Color(0xFF8FFFC2)),
        ),
      ),
    );
  }

  Widget glowCircle(double size, Color color) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color.withOpacity(.25),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(.45),
            blurRadius: 65,
            spreadRadius: 15,
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Background gradient
          const Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF063B2A),
                    Color(0xFF087A4B),
                    Color(0xFF13A86A),
                    Color(0xFF06452F),
                  ],
                ),
              ),
            ),
          ),

          // Blurred glowing circles
          Positioned(
            top: -100,
            right: -90,
            child: glowCircle(280, const Color(0xFF7CFFB2)),
          ),
          Positioned(
            bottom: 80,
            left: -100,
            child: glowCircle(250, const Color(0xFF00E5A0)),
          ),

          // CINEMATIC RICE INTRO
          AnimatedBuilder(
            animation: introController,
            builder: (context, child) {
              final opacity = (1.0 - (introController.value - .62).clamp(0.0, 1.0))
                  .clamp(0.0, 1.0);

              return IgnorePointer(
                child: Opacity(
                  opacity: opacity,
                  child: Center(
                    child: Transform.scale(
                      scale: introScale.value,
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Container(
                            width: 190,
                            height: 190,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: const Color(0xFF9AFFC8).withOpacity(.08),
                              border: Border.all(
                                color: Colors.white.withOpacity(.2),
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFF6CFFB2)
                                      .withOpacity(.4),
                                  blurRadius: 70,
                                  spreadRadius: 10,
                                ),
                              ],
                            ),
                            child: const Center(
                              child: RiceCinematic(),
                            ),
                          ),
                          const SizedBox(height: 24),
                          const Text(
                            'NÔNG NGHIỆP XANH',
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 22,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 3,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'SMART FARMING • GREEN FUTURE',
                            style: TextStyle(
                              color: Colors.white.withOpacity(.7),
                              fontSize: 10,
                              letterSpacing: 2,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),

          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 24,
                ),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: FadeTransition(
                    opacity: formOpacity,
                    child: SlideTransition(
                      position: formSlide,
                      child: FadeTransition(
                        opacity: fade,
                        child: SlideTransition(
                          position: slide,
                          child: Column(
                        children: [
                          // Logo
                          glass(
                            radius: 30,
                            child: const Padding(
                              padding: EdgeInsets.all(18),
                              child: Icon(
                                Icons.eco_rounded,
                                size: 48,
                                color: Color(0xFFB9FFD8),
                              ),
                            ),
                          ),

                          const SizedBox(height: 14),

                          const Text(
                            'NÔNG NGHIỆP XANH',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 23,
                              fontWeight: FontWeight.w900,
                              letterSpacing: 1.5,
                            ),
                          ),

                          const SizedBox(height: 5),

                          Text(
                            'Công nghệ xanh • Tương lai xanh',
                            style: TextStyle(
                              color: Colors.white.withOpacity(.7),
                              fontSize: 12,
                              letterSpacing: 1,
                            ),
                          ),

                          const SizedBox(height: 24),

                          // Animated rice illustration
                          SizedBox(
                            height: 165,
                            child: AnimatedBuilder(
                              animation: riceController,
                              builder: (context, child) {
                                final angle =
                                    (riceController.value - .5) * .10;

                                return Stack(
                                  alignment: Alignment.center,
                                  children: [
                                    glowCircle(
                                      125,
                                      const Color(0xFF9AFFC8),
                                    ),
                                    Container(
                                      width: 135,
                                      height: 135,
                                      decoration: BoxDecoration(
                                        shape: BoxShape.circle,
                                        color: Colors.white.withOpacity(.08),
                                        border: Border.all(
                                          color: Colors.white.withOpacity(.22),
                                        ),
                                      ),
                                    ),
                                    Positioned(
                                      bottom: 5,
                                      child: Transform.rotate(
                                        angle: angle,
                                        alignment: Alignment.bottomCenter,
                                        child: const Icon(
                                          Icons.grass_rounded,
                                          size: 125,
                                          color: Color(0xFFB9FFD8),
                                        ),
                                      ),
                                    ),
                                    Positioned(
                                      top: 15,
                                      right: 75,
                                      child: Icon(
                                        Icons.auto_awesome,
                                        size: 22,
                                        color: Colors.white.withOpacity(.8),
                                      ),
                                    ),
                                    Positioned(
                                      bottom: 28,
                                      left: 65,
                                      child: Icon(
                                        Icons.eco_rounded,
                                        size: 25,
                                        color: const Color(0xFF9AFFC8),
                                      ),
                                    ),
                                  ],
                                );
                              },
                            ),
                          ),

                          const SizedBox(height: 12),

                          AnimatedSwitcher(
                            duration: const Duration(milliseconds: 400),
                            transitionBuilder: (child, animation) =>
                                FadeTransition(
                              opacity: animation,
                              child: SlideTransition(
                                position: Tween<Offset>(
                                  begin: const Offset(0, .12),
                                  end: Offset.zero,
                                ).animate(animation),
                                child: child,
                              ),
                            ),
                            child: Text(
                              registering ? 'Create Account' : 'Welcome Back',
                              key: ValueKey(registering),
                              textAlign: TextAlign.center,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 30,
                                fontWeight: FontWeight.w800,
                                letterSpacing: -.5,
                              ),
                            ),
                          ),

                          const SizedBox(height: 8),

                          Text(
                            registering
                                ? 'Bắt đầu hành trình nông nghiệp thông minh'
                                : 'Đăng nhập để tiếp tục hành trình xanh',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white.withOpacity(.72),
                              fontSize: 13,
                            ),
                          ),

                          const SizedBox(height: 25),

                          // Glass login form
                          glass(
                            child: Padding(
                              padding: const EdgeInsets.all(22),
                              child: Column(
                                children: [
                                  input(
                                    controller: username,
                                    label: 'Tên tài khoản',
                                    icon: Icons.person_outline_rounded,
                                  ),

                                  const SizedBox(height: 16),

                                  input(
                                    controller: password,
                                    label: 'Mật khẩu',
                                    icon: Icons.lock_outline_rounded,
                                    passwordField: true,
                                  ),

                                  if (registering)
                                    const Padding(
                                      padding: EdgeInsets.only(top: 10),
                                      child: Text(
                                        'Tên tài khoản 3–24 ký tự • Mật khẩu 10–128 ký tự',
                                        style: TextStyle(
                                          color: Colors.white70,
                                          fontSize: 11,
                                        ),
                                      ),
                                    ),

                                  if (error != null) ...[
                                    const SizedBox(height: 14),
                                    Text(
                                      error!,
                                      textAlign: TextAlign.center,
                                      style: const TextStyle(
                                        color: Color(0xFFFFB9B9),
                                        fontSize: 13,
                                      ),
                                    ),
                                  ],

                                  const SizedBox(height: 22),

                                  // Gradient button
                                  SizedBox(
                                    width: double.infinity,
                                    height: 56,
                                    child: DecoratedBox(
                                      decoration: BoxDecoration(
                                        gradient: const LinearGradient(
                                          colors: [
                                            Color(0xFF9CFFC7),
                                            Color(0xFF35D98B),
                                          ],
                                        ),
                                        borderRadius: BorderRadius.circular(18),
                                        boxShadow: [
                                          BoxShadow(
                                            color: green.withOpacity(.35),
                                            blurRadius: 20,
                                            offset: const Offset(0, 8),
                                          ),
                                        ],
                                      ),
                                      child: ElevatedButton(
                                        onPressed: busy ? null : submit,
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: Colors.transparent,
                                          shadowColor: Colors.transparent,
                                          shape: RoundedRectangleBorder(
                                            borderRadius:
                                                BorderRadius.circular(18),
                                          ),
                                        ),
                                        child: busy
                                            ? const SizedBox(
                                                width: 23,
                                                height: 23,
                                                child:
                                                    CircularProgressIndicator(
                                                  color: darkGreen,
                                                  strokeWidth: 2,
                                                ),
                                              )
                                            : Text(
                                                registering
                                                    ? 'CREATE ACCOUNT'
                                                    : 'SIGN IN',
                                                style: const TextStyle(
                                                  color: darkGreen,
                                                  fontWeight: FontWeight.w900,
                                                  letterSpacing: 1.2,
                                                  fontSize: 15,
                                                ),
                                              ),
                                      ),
                                    ),
                                  ),

                                  const SizedBox(height: 18),

                                  // Switch login/register
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Text(
                                        registering
                                            ? 'Đã có tài khoản? '
                                            : 'Chưa có tài khoản? ',
                                        style: const TextStyle(
                                          color: Colors.white70,
                                          fontSize: 13,
                                        ),
                                      ),
                                      GestureDetector(
                                        onTap: busy
                                            ? null
                                            : () => setState(() {
                                                  registering = !registering;
                                                  error = null;
                                                }),
                                        child: Text(
                                          registering
                                              ? 'Đăng nhập'
                                              : 'Đăng ký',
                                          style: const TextStyle(
                                            color: Color(0xFFB9FFD8),
                                            fontWeight: FontWeight.bold,
                                            fontSize: 13,
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          ),

                          const SizedBox(height: 22),

                          Text(
                            '© Nông Nghiệp Xanh • Smart Farming',
                            style: TextStyle(
                              color: Colors.white.withOpacity(.45),
        fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
            ),
        ],
      ),
    );
  }
}
