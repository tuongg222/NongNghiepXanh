from pathlib import Path

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

if "import '../widgets/rice_cinematic.dart';" not in s:
    s = s.replace(
        "import '../services/auth_service.dart';",
        "import '../services/auth_service.dart';\nimport '../widgets/rice_cinematic.dart';"
    )

old = """                            child: const Center(
                              child: Icon(
                                Icons.grass_rounded,
                                size: 145,
                                color: Color(0xFFB9FFD8),
                              ),
                            ),"""

new = """                            child: const Center(
                              child: RiceCinematic(),
                            ),"""

if old not in s:
    print("KHONG TIM THAY ICON INTRO - khong sua file")
else:
    s = s.replace(old, new, 1)
    p.write_text(s)
    print("DA GHÉP RICE CINEMATIC VÀO INTRO")
