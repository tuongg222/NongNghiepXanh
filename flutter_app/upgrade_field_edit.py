from pathlib import Path
import sys

p = Path("lib/screens/field_map_screen.dart")
s = p.read_text()

if "int? selectedPoint" in s:
    sys.exit("STOP: Đã có chức năng chỉnh điểm.")

backup = Path("lib/screens/field_map_screen.dart.bak_edit")
if backup.exists():
    sys.exit("STOP: Backup đã tồn tại.")

checks = [
    "void addPoint(LatLng p)",
    "void undo()",
    "MarkerLayer(",
    "onTap: (_, point) => addPoint(point),",
]
for c in checks:
    if c not in s:
        sys.exit("STOP: Không tìm thấy cấu trúc: " + c)

backup.write_text(s)

s = s.replace(
    "bool satelliteMode = false;",
    "bool satelliteMode = false;\n  int? selectedPoint;",
    1,
)

s = s.replace(
    "void addPoint(LatLng p) {\n    setState(() => points.add(p));\n  }",
    """void addPoint(LatLng p) {
    setState(() {
      if (selectedPoint != null &&
          selectedPoint! >= 0 &&
          selectedPoint! < points.length) {
        points[selectedPoint!] = p;
        selectedPoint = null;
      } else {
        points.add(p);
      }
    });
  }

  void selectPoint(int index) {
    setState(() => selectedPoint = index);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Đã chọn điểm ${index + 1}. Chạm bản đồ để đổi vị trí.',
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }""",
    1,
)

s = s.replace(
    "onTap: (_, point) => addPoint(point),",
    "onTap: (_, point) => addPoint(point),",
    1,
)

old = """                      child: Container(
                        decoration: BoxDecoration(
                          color: Colors.green,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                        ),
                        child: Center(
                          child: Text(
                            '${entry.key + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),"""

new = """                      child: GestureDetector(
                        onLongPress: () => selectPoint(entry.key),
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 180),
                          decoration: BoxDecoration(
                            color: selectedPoint == entry.key
                                ? Colors.orange
                                : Colors.green,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white,
                              width: selectedPoint == entry.key ? 4 : 3,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: (selectedPoint == entry.key
                                        ? Colors.orange
                                        : Colors.green)
                                    .withOpacity(.35),
                                blurRadius: 12,
                              ),
                            ],
                          ),
                          child: Center(
                            child: Text(
                              '${entry.key + 1}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                      ),"""

if old not in s:
    sys.exit("STOP: Không khớp marker hiện tại.")

s = s.replace(old, new, 1)

s = s.replace(
    "'Chạm bản đồ để thêm điểm ranh giới. '\n                  'Cần tối thiểu 3 điểm để tính diện tích.'",
    "'Chạm bản đồ để thêm điểm. Nhấn giữ điểm để chọn '\n                  'rồi chạm vị trí mới để chỉnh ranh giới.'",
    1,
)

p.write_text(s)
print("OK: Đã thêm chọn và chỉnh vị trí điểm ranh giới.")
print("Backup:", backup)
