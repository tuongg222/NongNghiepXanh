from pathlib import Path

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

old = """                  child: FadeTransition(
                    opacity: formOpacity,
                    child: SlideTransition(
                      position: formSlide,
                      child: FadeTransition(
                    opacity: fade,
                    child: FadeTransition(
                      opacity: formOpacity,
                      child: SlideTransition(
                        position: formSlide,
                      child: Column("""
new = """                  child: FadeTransition(
                    opacity: formOpacity,
                    child: SlideTransition(
                      position: formSlide,
                      child: FadeTransition(
                        opacity: fade,
                        child: SlideTransition(
                          position: slide,
                          child: Column("""

if old not in s:
    print("KHONG TIM THAY DOAN CAN SUA")
    print("Khong ghi file.")
    raise SystemExit(1)

s = s.replace(old, new, 1)

p.write_text(s)
print("DA SUA FORM TRANSITION")
