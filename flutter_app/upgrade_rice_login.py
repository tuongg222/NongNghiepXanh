from pathlib import Path
import shutil
from datetime import datetime

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

old = """  late final AnimationController animationController;
  late final Animation<double> fade;
  late final Animation<Offset> slide;
"""

new = """  late final AnimationController animationController;
  late final AnimationController riceController;
  late final Animation<double> fade;
  late final Animation<Offset> slide;
"""

if old not in s:
    raise SystemExit("Không tìm thấy phần khai báo animation. Dừng!")

s = s.replace(old, new, 1)

old_init = """    animationController.forward();
"""

new_init = """    animationController.forward();

    riceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2200),
    )..repeat(reverse: true);
"""

if old_init not in s:
    raise SystemExit("Không tìm thấy animationController.forward(). Dừng!")

s = s.replace(old_init, new_init, 1)

old_dispose = """    animationController.dispose();
    username.dispose();
"""

new_dispose = """    animationController.dispose();
    riceController.dispose();
    username.dispose();
"""

if old_dispose not in s:
    raise SystemExit("Không tìm thấy dispose(). Dừng!")

s = s.replace(old_dispose, new_dispose, 1)

start = s.find("                          // Farmer illustration")
end = s.find("                          const SizedBox(height: 12),", start)

if start == -1 or end == -1:
    raise SystemExit("Không tìm thấy khu vực minh họa nông dân. Dừng!")

rice = """                          // Animated rice illustration
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

"""

s = s[:start] + rice + s[end:]

backup = p.with_suffix(".dart.bak_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
shutil.copy2(p, backup)
p.write_text(s)

print("Đã nâng cấp hình cây lúa animation!")
print("Backup:", backup)
