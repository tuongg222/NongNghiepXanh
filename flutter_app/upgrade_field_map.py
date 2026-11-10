from pathlib import Path
import sys

p = Path("lib/screens/field_map_screen.dart")
s = p.read_text()

checks = [
    "class _FieldMapScreenState extends State<FieldMapScreen>",
    "TileLayer(",
    "DIỆN TÍCH THỬA ĐẤT",
    "void addPoint(LatLng p)",
]
for marker in checks:
    if marker not in s:
        sys.exit("STOP: Không tìm thấy " + marker)

if "bool satelliteMode" in s:
    sys.exit("STOP: Bản đồ đã được nâng cấp.")

backup = Path("lib/screens/field_map_screen.dart.bak_satellite")
if backup.exists():
    sys.exit("STOP: Backup đã tồn tại.")

backup.write_text(s)

# Trạng thái bản đồ và công đất
s = s.replace(
    "bool locating = false;",
    """bool locating = false;
  bool satelliteMode = false;
  double congM2 = 1000;""",
1)

# Tổng chu vi
s = s.replace(
    "String fmt(double m) {",
    """double get perimeter {
    if (points.length < 2) return 0;
    double total = 0;
    for (int i = 0; i < points.length; i++) {
      total += distance(points[i], points[(i + 1) % points.length]);
    }
    return total;
  }

  String fmt(double m) {""",
1)

# Nút chuyển bản đồ
s = s.replace(
    """        actions: [
          IconButton(
            onPressed: undo,""",
    """        actions: [
          IconButton(
            tooltip: satelliteMode ? 'Bản đồ đường phố' : 'Bản đồ vệ tinh',
            onPressed: () => setState(() => satelliteMode = !satelliteMode),
            icon: Icon(
              satelliteMode ? Icons.map_rounded : Icons.satellite_alt_rounded,
            ),
          ),
          IconButton(
            onPressed: undo,""",
1)

# Thay lớp bản đồ
old = """                TileLayer(
                  urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.nongnghiep.xanh',
                ),"""
new = """                TileLayer(
                  urlTemplate: satelliteMode
                      ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
                      : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.nongnghiep.xanh',
                  tileProvider: NetworkTileProvider(),
                ),"""
if old not in s:
    sys.exit("STOP: Không tìm thấy TileLayer cũ.")

s = s.replace(old, new, 1)

# Hiển thị quy đổi công đất và chu vi
old = """                Text(
                  '${(area / 10000).toStringAsFixed(4)} ha'
                  ' • ${(area / 1000).toStringAsFixed(3)} công (1 công = 1.000 m²)',
                  style: const TextStyle(color: Colors.black54),
                ),"""
new = """                Text(
                  '${(area / 10000).toStringAsFixed(4)} ha'
                  ' • ${(area / congM2).toStringAsFixed(3)} công',
                  style: const TextStyle(color: Colors.black54),
                ),
                const SizedBox(height: 8),
                Wrap(
                  crossAxisAlignment: WrapCrossAlignment.center,
                  spacing: 10,
                  children: [
                    const Text('Quy ước công:'),
                    DropdownButton<double>(
                      value: congM2,
                      items: const [
                        DropdownMenuItem(
                          value: 1000,
                          child: Text('1.000 m²'),
                        ),
                        DropdownMenuItem(
                          value: 1296,
                          child: Text('1.296 m²'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) setState(() => congM2 = value);
                      },
                    ),
                  ],
                ),
                Text(
                  'Chu vi: ${fmt(perimeter)}',
                  style: const TextStyle(
                    color: Color(0xFF167A45),
                    fontWeight: FontWeight.w700,
                  ),
                ),"""
if old not in s:
    sys.exit("STOP: Không tìm thấy phần quy đổi công cũ.")

s = s.replace(old, new, 1)
p.write_text(s)

print("OK: Đã thêm bản đồ vệ tinh, quy đổi công và chu vi.")
print("Backup:", backup)
