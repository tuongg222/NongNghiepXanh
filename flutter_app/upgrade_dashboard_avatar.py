from pathlib import Path
import sys

p = Path("lib/screens/home_screen.dart")
s = p.read_text()

old = """                      Container(
                        width: 53,
                        height: 53,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(.18),
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(color: Colors.white24),
                        ),
                        child: const Icon(
                          Icons.person_rounded,
                          color: Colors.white,
                          size: 30,
                        ),
                      ),"""

new = """                      TweenAnimationBuilder<double>(
                        tween: Tween(begin: .88, end: 1),
                        duration: const Duration(milliseconds: 750),
                        curve: Curves.easeOutBack,
                        builder: (context, scale, child) {
                          return Transform.scale(
                            scale: scale,
                            child: child,
                          );
                        },
                        child: Container(
                          width: 62,
                          height: 62,
                          decoration: BoxDecoration(
                            gradient: const LinearGradient(
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                              colors: [
                                Color(0xFFB8F5D2),
                                Color(0xFF37C982),
                                Color(0xFF087647),
                              ],
                            ),
                            borderRadius: BorderRadius.circular(21),
                            border: Border.all(
                              color: Colors.white.withOpacity(.65),
                              width: 1.5,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: const Color(0xFF8BFFC0).withOpacity(.32),
                                blurRadius: 20,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.person_rounded,
                            color: Colors.white,
                            size: 35,
                          ),
                        ),
                      ),"""

if old not in s:
    sys.exit("STOP: Không tìm thấy avatar cũ. File chưa bị sửa.")

backup = Path("lib/screens/home_screen.dart.bak_avatar")
if backup.exists():
    sys.exit("STOP: Backup đã tồn tại, không ghi đè.")

backup.write_text(s)
s = s.replace(old, new, 1)
p.write_text(s)

print("OK: Đã nâng cấp avatar Dashboard.")
print("Backup:", backup)
