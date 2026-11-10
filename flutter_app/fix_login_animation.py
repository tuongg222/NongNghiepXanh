from pathlib import Path

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

old = """                  child: FadeTransition(
                    opacity: fade,
                    child: FadeTransition(
                      opacity: formOpacity,
                      child: SlideTransition(
                        position: formSlide,"""

if old not in s:
    print("Không tìm thấy đoạn animation lồng nhau.")
    print("Không thay đổi file.")
    raise SystemExit

print("Đã tìm thấy animation form.")
print("File đang có fade + slide intro.")
