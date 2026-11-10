from pathlib import Path
import shutil
import re

p = Path("lib/screens/login_screen.dart")
src = p.read_text()

# Backup
backup = p.with_suffix(".dart.backup")
shutil.copy2(p, backup)
print("Backup:", backup)

# Add intro animation controllers
if "introController" not in src:
    src = src.replace(
        "late final AnimationController riceController;",
        """late final AnimationController riceController;
  late final AnimationController introController;
  late final Animation<double> introScale;
  late final Animation<double> formOpacity;
  late final Animation<Offset> formSlide;
  bool introFinished = false;"""
    )

    src = src.replace(
        "animationController.forward();",
        """animationController.forward();

    introController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 3200),
    );

    introScale = Tween<double>(
      begin: 0.12,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: introController,
      curve: Curves.easeOutCubic,
    ));

    formOpacity = CurvedAnimation(
      parent: introController,
      curve: const Interval(.58, 1.0, curve: Curves.easeIn),
    );

    formSlide = Tween<Offset>(
      begin: const Offset(0, .18),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: introController,
      curve: const Interval(.58, 1.0, curve: Curves.easeOutCubic),
    ));

    introController.forward().whenComplete(() {
      if (mounted) setState(() => introFinished = true);
    });"""
    )

    src = src.replace(
        "riceController.dispose();",
        "riceController.dispose();\\n    introController.dispose();"
    )

# Replace build method
start = src.find("  @override\\n  Widget build(BuildContext context)")
if start < 0:
    raise SystemExit("Không tìm thấy build()")

# Find build method's opening brace and match closing brace
brace = src.find("{", start)
depth = 0
end = -1
for i in range(brace, len(src)):
    if src[i] == "{":
        depth += 1
    elif src[i] == "}":
        depth -= 1
        if depth == 0:
            end = i + 1
            break

if end < 0:
    raise SystemExit("Không xác định được cuối build()")

new_build = r'''
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          const DecoratedBox(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [
                  Color(0xFF021D15),
                  Color(0xFF064E35),
                  Color(0xFF087A4B),
                  Color(0xFF031F17),
                ],
              ),
            ),
          ),

          Positioned(
            top: -100,
            right: -80,
            child: glowCircle(280, const Color(0xFF7CFFB2)),
          ),
          Positioned(
            bottom: -80,
            left: -100,
            child: glowCircle(280, const Color(0xFF00E5A0)),
          ),

          // Cinematic rice intro
          AnimatedBuilder(
            animation: introController,
            builder: (context, child) {
              final t = introController.value;
              final scale = introScale.value;
              final opacity = (1 - (t > .55 ? (t - .55) / .45 : 0))
                  .clamp(0.0, 1.0);

              return Center(
                child: Opacity(
                  opacity: opacity,
                  child: Transform.scale(
                    scale: scale,
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
                              color: Colors.white.withOpacity(.22),
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF6CFFB2)
                                    .withOpacity(.35),
                                blurRadius: 70,
                                spreadRadius: 12,
                              ),
                            ],
                          ),
                          child: const Center(
                            child: Icon(
                              Icons.grass_rounded,
                              size: 145,
                              color: Color(0xFFB9FFD8),
                            ),
                          ),
                        ),
                        const SizedBox(height: 24),
                        const Text(
                          'NÔNG NGHIỆP XANH',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 23,
                            fontWeight: FontWeight.w900,
                            letterSpacing: 3,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'SMART FARMING • GREEN FUTURE',
                          style: TextStyle(
                            color: Colors.white.withOpacity(.65),
                            fontSize: 10,
                            letterSpacing: 2.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            },
          ),

          // Login interface appears after the intro
          SafeArea(
            child: Center(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 20,
                ),
                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: AnimatedBuilder(
                    animation: introController,
                    builder: (context, child) {
                      return Opacity(
                        opacity: formOpacity.value,
                        child: SlideTransition(
                          position: formSlide,
                          child: child,
                        ),
                      );
                    },
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(30),
                      child: BackdropFilter(
                        filter: ImageFilter.blur(
                          sigmaX: introFinished ? 0 : 14,
                          sigmaY: introFinished ? 0 : 14,
                        ),
                        child: Column(
                          children: [
                            const Icon(
                              Icons.eco_rounded,
                              size: 48,
                              color: Color(0xFFB9FFD8),
                            ),
                            const SizedBox(height: 12),
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
                            const SizedBox(height: 6),
                            Text(
                              'Công nghệ xanh • Tương lai xanh',
                              style: TextStyle(
                                color: Colors.white.withOpacity(.7),
                                fontSize: 12,
                              ),
                            ),
                            const SizedBox(height: 24),

                            glass(
                              radius: 28,
                              child: Padding(
                                padding: const EdgeInsets.all(22),
                                child: Column(
                                  children: [
                                    AnimatedSwitcher(
                                      duration: const Duration(
                                        milliseconds: 450,
                                      ),
                                      child: Text(
                                        registering
                                            ? 'Create Account'
                                            : 'Welcome Back',
                                        key: ValueKey(registering),
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 29,
                                          fontWeight: FontWeight.w800,
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
                                          borderRadius:
                                              BorderRadius.circular(18),
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
                                            backgroundColor:
                                                Colors.transparent,
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
                                                    fontWeight:
                                                        FontWeight.w900,
                                                    letterSpacing: 1.2,
                                                    fontSize: 15,
                                                  ),
                                                ),
                                        ),
                                      ),
                                    ),
                                    const SizedBox(height: 18),
                                    Row(
                                      mainAxisAlignment:
                                          MainAxisAlignment.center,
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
                                                    registering =
                                                        !registering;
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
        ],
      ),
    );
  }
'''

src = src[:start] + new_build + src[end:]
p.write_text(src)
print("Đã nâng cấp LoginScreen!")
print("Backup cũ:", backup)
