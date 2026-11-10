import 'dart:ui';
import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import '../services/weather_service.dart';
import 'diagnose_screen.dart';
import 'field_map_screen.dart';
import 'login_screen.dart';
import 'journal_screen.dart';

const nxGreen = Color(0xFF167A45);
const nxDark = Color(0xFF103D29);

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  Map<String, dynamic>? weather;
  bool loading = true;
  String backendStatus = 'Đang kết nối...';
  String locationName = 'Cần Thơ / An Giang';

  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    setState(() => loading = true);
    try {
      final results = await Future.wait([
        WeatherService.current(),
        ApiService.health(),
      ]);
      weather = results[0];
      backendStatus = results[1]['aiConnected'] == true
          ? 'AI đang sẵn sàng'
          : 'Backend hoạt động';
    } catch (_) {
      backendStatus = 'Không kết nối được máy chủ';
    }
    if (mounted) setState(() => loading = false);
  }

  void openFeature(String title, String description) {
    Navigator.of(context).push(
      PageRouteBuilder(
        transitionDuration: const Duration(milliseconds: 350),
        pageBuilder: (_, animation, secondaryAnimation) =>
            FeaturePlaceholder(title: title, description: description),
        transitionsBuilder: (_, animation, secondaryAnimation, child) {
          final curved = CurvedAnimation(
            parent: animation,
            curve: Curves.easeOutCubic,
          );
          return FadeTransition(
            opacity: curved,
            child: SlideTransition(
              position: Tween<Offset>(
                begin: const Offset(0, .035),
                end: Offset.zero,
              ).animate(curved),
              child: child,
            ),
          );
        },
      ),
    );
  }

  Future<void> logout() async {
    await AuthService.logout();
    if (!mounted) return;
    Navigator.of(context).pushAndRemoveUntil(
      PageRouteBuilder(
        pageBuilder: (_, __, ___) => const LoginScreen(),
        transitionsBuilder: (_, animation, __, child) =>
            FadeTransition(opacity: animation, child: child),
      ),
      (_) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final current = weather?['current'] as Map<String, dynamic>?;
    final username = AuthService.user?['username'] ?? 'Nhà nông';

    return Scaffold(
      backgroundColor: const Color(0xFFF2F7F3),
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          SliverToBoxAdapter(
            child: Container(
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 18,
                left: 22,
                right: 22,
                bottom: 28,
              ),
              decoration: const BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color(0xFF064E35),
                    Color(0xFF13864F),
                    Color(0xFF29A86A),
                  ],
                ),
                borderRadius: BorderRadius.vertical(
                  bottom: Radius.circular(34),
                ),
              ),
              child: Column(
                children: [
                  Row(
                    children: [
                      const Icon(Icons.eco, color: Colors.white, size: 30),
                      const SizedBox(width: 9),
                      const Expanded(
                        child: Text(
                          'Nông Nghiệp Xanh',
                          style: TextStyle(
                            color: Colors.white,
                            fontSize: 19,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ),
                      _AnimatedIconButton(
                        icon: Icons.logout_rounded,
                        onTap: logout,
                      ),
                    ],
                  ),
                  const SizedBox(height: 25),
                  Row(
                    children: [
                      Container(
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
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Xin chào nhà nông 👋',
                              style: TextStyle(color: Colors.white70),
                            ),
                            Text(
                              username.toString(),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 23,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 23),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(23),
                    child: BackdropFilter(
                      filter: ImageFilter.blur(sigmaX: 15, sigmaY: 15),
                      child: Container(
                        padding: const EdgeInsets.all(17),
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(.13),
                          border: Border.all(color: Colors.white24),
                          borderRadius: BorderRadius.circular(23),
                        ),
                        child: Row(
                          children: [
                            const Icon(
                              Icons.wb_sunny_rounded,
                              color: Color(0xFFFFE59B),
                              size: 42,
                            ),
                            const SizedBox(width: 14),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    locationName,
                                    style: const TextStyle(
                                      color: Colors.white70,
                                      fontSize: 12,
                                    ),
                                  ),
                                  loading
                                      ? const Text(
                                          'Đang tải thời tiết...',
                                          style: TextStyle(color: Colors.white),
                                        )
                                      : current == null
                                          ? const Text(
                                              'Chưa có dữ liệu',
                                              style: TextStyle(color: Colors.white),
                                            )
                                          : Text(
                                              '${current['temperature_2m']}°C',
                                              style: const TextStyle(
                                                color: Colors.white,
                                                fontSize: 27,
                                                fontWeight: FontWeight.bold,
                                              ),
                                            ),
                                  if (current != null)
                                    Text(
                                      'Độ ẩm ${current['relative_humidity_2m']}% • Gió ${current['wind_speed_10m']} km/h',
                                      style: const TextStyle(
                                        color: Colors.white70,
                                        fontSize: 11,
                                      ),
                                    ),
                                ],
                              ),
                            ),
                            IconButton(
                              onPressed: refresh,
                              icon: const Icon(
                                Icons.refresh_rounded,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    backendStatus,
                    style: const TextStyle(color: Colors.white70, fontSize: 11),
                  ),
                ],
              ),
            ),
          ),

          SliverPadding(
            padding: const EdgeInsets.fromLTRB(20, 24, 20, 30),
            sliver: SliverToBoxAdapter(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Nông trại của bạn',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: nxDark,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Quản lý thông minh • Mùa vụ hiệu quả',
                    style: TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 18),

                  _FeatureCard(
                    icon: Icons.document_scanner_rounded,
                    title: 'AI chẩn đoán cây trồng',
                    subtitle: 'Chụp ảnh • Phân tích • Tư vấn chăm sóc',
                    color: const Color(0xFF15945A),
                    large: true,
                    onTap: () => Navigator.push(
                      context,
                      _smoothRoute(const DiagnoseScreen()),
                    ),
                  ),

                  const SizedBox(height: 12),

                  Row(
                    children: [
                      Expanded(
                        child: _FeatureCard(
                          icon: Icons.map_rounded,
                          title: 'Bản đồ GPS',
                          subtitle: 'Đo diện tích ruộng',
                          color: const Color(0xFF3986D8),
                          onTap: () => openFeature(
                            'Bản đồ GPS',
                            'Định vị, đánh dấu ranh giới và đo diện tích đất.',
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _FeatureCard(
                          icon: Icons.grass_rounded,
                          title: 'Mùa vụ',
                          subtitle: 'Theo dõi cây trồng',
                          color: const Color(0xFF8C9F32),
                          onTap: () => openFeature(
                            'Quản lý mùa vụ',
                            'Tạo mùa vụ, ngày gieo, chăm sóc và thu hoạch.',
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 12),

                  Row(
                    children: [
                      Expanded(
                        child: _FeatureCard(
                          icon: Icons.menu_book_rounded,
                          title: 'Nhật ký',
                          subtitle: 'Ghi hoạt động',
                          color: const Color(0xFF9A65C8),
                          onTap: () => Navigator.push(
                            context,
                            _smoothRoute(const JournalScreen()),
                          ),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _FeatureCard(
                          icon: Icons.trending_up_rounded,
                          title: 'Giá nông sản',
                          subtitle: 'Theo dõi thị trường',
                          color: const Color(0xFFE19A36),
                          onTap: () => openFeature(
                            'Giá nông sản',
                            'Theo dõi giá lúa và các nông sản theo khu vực.',
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 22),

                  Container(
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(22),
                      border: Border.all(color: Colors.green.withOpacity(.08)),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.lightbulb_outline, color: nxGreen),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Text(
                            'Mẹo nhà nông\nTheo dõi thời tiết trước khi tưới hoặc phun thuốc.',
                            style: TextStyle(fontSize: 13, height: 1.5),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

Route<T> _smoothRoute<T>(Widget page) {
  return PageRouteBuilder<T>(
    transitionDuration: const Duration(milliseconds: 380),
    pageBuilder: (_, __, ___) => page,
    transitionsBuilder: (_, animation, __, child) {
      final curved = CurvedAnimation(
        parent: animation,
        curve: Curves.easeOutCubic,
      );
      return FadeTransition(
        opacity: curved,
        child: SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, .04),
            end: Offset.zero,
          ).animate(curved),
          child: child,
        ),
      );
    },
  );
}

class _AnimatedIconButton extends StatefulWidget {
  final IconData icon;
  final VoidCallback onTap;

  const _AnimatedIconButton({
    required this.icon,
    required this.onTap,
  });

  @override
  State<_AnimatedIconButton> createState() => _AnimatedIconButtonState();
}

class _AnimatedIconButtonState extends State<_AnimatedIconButton> {
  bool pressed = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTapDown: (_) => setState(() => pressed = true),
      onTapUp: (_) => setState(() => pressed = false),
      onTapCancel: () => setState(() => pressed = false),
      onTap: widget.onTap,
      child: AnimatedScale(
        scale: pressed ? .88 : 1,
        duration: const Duration(milliseconds: 150),
        child: Container(
          width: 43,
          height: 43,
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(.14),
            borderRadius: BorderRadius.circular(15),
            border: Border.all(color: Colors.white24),
          ),
          child: Icon(widget.icon, color: Colors.white),
        ),
      ),
    );
  }
}

class _FeatureCard extends StatefulWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final bool large;
  final VoidCallback onTap;

  const _FeatureCard({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
    this.large = false,
  });

  @override
  State<_FeatureCard> createState() => _FeatureCardState();
}

class _FeatureCardState extends State<_FeatureCard> {
  bool pressed = false;

  @override
  Widget build(BuildContext context) {
    return AnimatedScale(
      scale: pressed ? .965 : 1,
      duration: const Duration(milliseconds: 160),
      curve: Curves.easeOut,
      child: ClipRRect(
        borderRadius: BorderRadius.circular(23),
        child: BackdropFilter(
          filter: ImageFilter.blur(sigmaX: 12, sigmaY: 12),
          child: Material(
            color: Colors.white.withOpacity(.82),
            child: InkWell(
              onTap: widget.onTap,
              onHighlightChanged: (value) => setState(() => pressed = value),
              borderRadius: BorderRadius.circular(23),
              child: Container(
                constraints: BoxConstraints(
                  minHeight: widget.large ? 130 : 150,
                ),
                padding: const EdgeInsets.all(17),
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(23),
                  border: Border.all(color: widget.color.withOpacity(.12)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 45,
                      height: 45,
                      decoration: BoxDecoration(
                        color: widget.color.withOpacity(.12),
                        borderRadius: BorderRadius.circular(15),
                      ),
                      child: Icon(widget.icon, color: widget.color, size: 25),
                    ),
                    const SizedBox(height: 13),
                    Text(
                      widget.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.w800,
                        color: nxDark,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 5),
                    Text(
                      widget.subtitle,
                      style: const TextStyle(
                        color: Colors.black54,
                        fontSize: 11,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class FeaturePlaceholder extends StatelessWidget {
  final String title;
  final String description;

  const FeaturePlaceholder({
    super.key,
    required this.title,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF2F7F3),
      appBar: AppBar(title: Text(title)),
      body: Center(
      child: Padding(
          padding: const EdgeInsets.all(25),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.eco, size: 65, color: nxGreen),
              const SizedBox(height: 18),
              Text(
                title,
                style: const TextStyle(
                  fontSize: 23,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(description, textAlign: TextAlign.center),
              const SizedBox(height: 20),
              const Text(
                'Phân hệ đang chờ tích hợp dữ liệu.',
                style: TextStyle(color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
