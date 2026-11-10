from pathlib import Path
import re
import sys

p = Path("lib/screens/home_screen.dart")
s = p.read_text()

# Kiểm tra cấu trúc trước khi sửa
required = [
    "class _FeatureCardState extends State<_FeatureCard>",
    "class _AnimatedIconButtonState extends State<_AnimatedIconButton>",
    "Route<T> _smoothRoute<T>(Widget page)",
    "class HomeScreen extends StatefulWidget",
]
for marker in required:
    if marker not in s:
        sys.exit(f"STOP: Không tìm thấy cấu trúc: {marker}")

if "dashboardEntranceController" in s:
    sys.exit("Dashboard đã được nâng cấp trước đó. Không sửa lại.")

backup = p.with_suffix(".dart.bak_dashboard")
backup.write_text(s)

# Nâng cấp hiệu ứng chuyển trang
s = s.replace(
    "transitionDuration: const Duration(milliseconds: 380),",
    "transitionDuration: const Duration(milliseconds: 520),",
    1,
)

# Thêm animation xuất hiện cho từng FeatureCard
old = """class _FeatureCardState extends State<_FeatureCard> {
  bool pressed = false;

  @override
  Widget build(BuildContext context) {
    return AnimatedScale(
      scale: pressed ? .965 : 1,
      duration: const Duration(milliseconds: 160),
      curve: Curves.easeOut,
      child: ClipRRect("""
new = """class _FeatureCardState extends State<_FeatureCard>
    with SingleTickerProviderStateMixin {
  bool pressed = false;

  late final AnimationController dashboardEntranceController;
  late final Animation<double> dashboardFade;
  late final Animation<Offset> dashboardSlide;

  @override
  void initState() {
    super.initState();

    dashboardEntranceController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 650),
    );

    dashboardFade = CurvedAnimation(
      parent: dashboardEntranceController,
      curve: Curves.easeOut,
    );

    dashboardSlide = Tween<Offset>(
      begin: const Offset(0, .10),
      end: Offset.zero,
    ).animate(
      CurvedAnimation(
        parent: dashboardEntranceController,
        curve: Curves.easeOutCubic,
      ),
    );

    dashboardEntranceController.forward();
  }

  @override
  void dispose() {
    dashboardEntranceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: dashboardFade,
      child: SlideTransition(
        position: dashboardSlide,
        child: AnimatedScale(
      scale: pressed ? .955 : 1,
      duration: const Duration(milliseconds: 190),
      curve: Curves.easeOutCubic,
      child: ClipRRect("""
if old not in s:
    sys.exit("STOP: Không khớp phần FeatureCard, chưa ghi file.")

s = s.replace(old, new, 1)

# Đóng các widget mới ở cuối FeatureCard
old_end = """      ),
    );
  }
}

class FeaturePlaceholder"""
new_end = """      ),
        ),
      ),
    );
  }
}

class FeaturePlaceholder"""
if old_end not in s:
    sys.exit("STOP: Không khớp phần kết FeatureCard, chưa ghi file.")

s = s.replace(old_end, new_end, 1)

p.write_text(s)
print("OK: Dashboard đã được nâng cấp!")
print("Backup:", backup)
print("Đã thêm animation Fade + Slide + Scale cho FeatureCard.")
print("Đã tăng thời gian chuyển trang lên 520ms.")
