from pathlib import Path
import shutil

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

# Backup
backup = Path("lib/screens/login_screen.dart.v2.backup")
shutil.copy2(p, backup)

if "introController" in s:
    print("File đã có introController, không chèn lại.")
    raise SystemExit

# 1. Add intro animation fields
s = s.replace(
    "late final AnimationController riceController;",
    """late final AnimationController riceController;
  late final AnimationController introController;
  late final Animation<double> introScale;
  late final Animation<double> formOpacity;
  late final Animation<Offset> formSlide;"""
)

# 2. Add intro animation in initState
s = s.replace(
    "animationController.forward();",
    """animationController.forward();

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

    introController.forward();"""
)

# 3. Dispose controller
s = s.replace(
    "riceController.dispose();",
    "riceController.dispose();\\n    introController.dispose();"
)

# 4. Put intro rice animation over existing UI
marker = "          SafeArea("
if marker not in s:
    print("Không tìm thấy SafeArea.")
    raise SystemExit

intro = """          // CINEMATIC RICE INTRO
          AnimatedBuilder(
            animation: introController,
            builder: (context, child) {
              final t = introController.value;
              final opacity = (1.0 - (t - .62).clamp(0.0, 1.0))
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

"""

s = s.replace(marker, intro + marker, 1)

# 5. Animate existing login UI
s = s.replace(
    """child: FadeTransition(
                    opacity: fade,
                    child: SlideTransition(
                      position: slide,""",
    """child: FadeTransition(
                    opacity: fade,
                    child: FadeTransition(
                      opacity: formOpacity,
                      child: SlideTransition(
                        position: formSlide,"""
)

# Close added SlideTransition
s = s.replace(
    """                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }""",
    """                      ),
                    ),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }"""
)

p.write_text(s)
print("Đã nâng cấp intro login!")
print("Backup:", backup)
