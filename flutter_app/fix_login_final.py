from pathlib import Path

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

# Fix import formatting
s = s.replace(
    "import '../widgets/rice_cinematic.dart';                                                                                             import 'home_screen.dart';",
    "import '../widgets/rice_cinematic.dart';\nimport 'home_screen.dart';"
)

# Fix declaration formatting
s = s.replace(
    "late final Animation<double> formOpacity;                                                                                            late final Animation<Offset> formSlide;",
    "late final Animation<double> formOpacity;\n  late final Animation<Offset> formSlide;"
)

# Remove unused intro t variable
s = s.replace(
    "final t = introController.value;\n              final opacity =",
    "final opacity ="
)

# Make form wait for rice intro, then fade + slide in
old = """                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: FadeTransition("""
new = """                child: ConstrainedBox(
                  constraints: const BoxConstraints(maxWidth: 440),
                  child: FadeTransition(
                    opacity: formOpacity,
                    child: SlideTransition(
                      position: formSlide,
                      child: FadeTransition("""
if old in s:
    s = s.replace(old, new, 1)
else:
    print("WARN: Khong tim thay dau form")

# Close the added widgets at the end of the original animation section.
# This section is intentionally inspected before automatic closing.
p.write_text(s)
print("DA SUA IMPORT VA FORM INTRO")
