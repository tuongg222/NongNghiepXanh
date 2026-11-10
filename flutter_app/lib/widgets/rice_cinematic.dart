import 'dart:math' as math;
import 'package:flutter/material.dart';

class RiceCinematic extends StatefulWidget {
  const RiceCinematic({super.key});

  @override
  State<RiceCinematic> createState() => _RiceCinematicState();
}

class _RiceCinematicState extends State<RiceCinematic>
    with TickerProviderStateMixin {
  late final AnimationController growController;
  late final AnimationController windController;

  @override
  void initState() {
    super.initState();

    growController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2600),
    );

    windController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 4200),
    )..repeat();

    growController.forward();
  }

  @override
  void dispose() {
    growController.dispose();
    windController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([growController, windController]),
      builder: (_, __) {
        return CustomPaint(
          painter: _RicePainter(
            grow: Curves.easeOutCubic.transform(
              growController.value,
            ),
            wind: windController.value,
          ),
          size: Size.infinite,
        );
      },
    );
  }
}

class _RicePainter extends CustomPainter {
  final double grow;
  final double wind;

  _RicePainter({
    required this.grow,
    required this.wind,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final w = size.width;
    final h = size.height;

    canvas.save();
    canvas.translate(w / 2, h * 0.72);

    final sway = math.sin(wind * math.pi * 2) * 7;

    final glow = Paint()
      ..color = Color.lerp(
        const Color(0x0038D98A),
        const Color(0x6638D98A),
        grow,
      )!
      ..maskFilter = const MaskFilter.blur(
        BlurStyle.normal,
        30,
      );

    canvas.drawCircle(
      Offset(0, -45 * grow),
      65 * grow,
      glow,
    );

    final stemPaint = Paint()
      ..color = const Color(0xFF68C86B)
      ..strokeWidth = 4
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final leafPaint = Paint()
      ..color = const Color(0xFF8BE36C)
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round
      ..style = PaintingStyle.stroke;

    final goldPaint = Paint()
      ..color = const Color(0xFFFFD66B)
      ..style = PaintingStyle.fill;

    // Thân lúa mọc từ gốc lên.
    final stem = Path()
      ..moveTo(0, 0)
      ..cubicTo(
        -4,
        -35 * grow,
        sway * grow,
        -95 * grow,
        sway * grow,
        -150 * grow,
      );

    canvas.drawPath(stem, stemPaint);

    // Lá trái.
    final leftLeaf = Path()
      ..moveTo(0, -35 * grow)
      ..quadraticBezierTo(
        -30 * grow,
        -55 * grow,
        -65 * grow,
        -70 * grow,
      );

    canvas.drawPath(leftLeaf, leafPaint);

    // Lá phải.
    final rightLeaf = Path()
      ..moveTo(0, -65 * grow)
      ..quadraticBezierTo(
        30 * grow,
        -85 * grow,
        65 * grow,
        -105 * grow,
      );

    canvas.drawPath(rightLeaf, leafPaint);

    // Bông lúa.
    final headX = sway * grow;
    final headY = -150 * grow;

    final panicle = Path()
      ..moveTo(headX, headY)
      ..quadraticBezierTo(
        headX + 18 * grow,
        headY - 30 * grow,
        headX + 38 * grow,
        headY - 60 * grow,
      );

    canvas.drawPath(panicle, stemPaint);

    // Hạt lúa bung dần.
    for (int i = 0; i < 14; i++) {
      final progress = i / 14;
      final x = headX + 8 + progress * 32;
      final y = headY - 8 - progress * 48;

      canvas.save();
      canvas.translate(x * grow, y * grow);
      canvas.rotate(-0.45 + progress * 0.5);

      final grain = RRect.fromRectAndRadius(
        Rect.fromCenter(
          center: Offset.zero,
          width: 7 * grow,
          height: 14 * grow,
        ),
        Radius.circular(5 * grow),
      );

      canvas.drawRRect(grain, goldPaint);
      canvas.restore();
    }

    // Hạt sáng.
    for (int i = 0; i < 18; i++) {
      final angle = wind * math.pi * 2 + i * math.pi / 9;
      final radius = 70 + 15 * math.sin(angle * 2);

      final x = math.cos(angle) * radius;
      final y = math.sin(angle) * radius - 40;

      final particlePaint = Paint()
        ..color = Color.lerp(
          const Color(0xFF6CE6A0),
          const Color(0xFFFFD66B),
          (i % 4) / 3,
        )!;

      canvas.drawCircle(
        Offset(x, y),
        1.8 + (i % 3) * 0.5,
        particlePaint,
      );
    }

    canvas.restore();
  }

  @override
  bool shouldRepaint(covariant _RicePainter oldDelegate) {
    return oldDelegate.grow != grow ||
        oldDelegate.wind != wind;
  }
}
