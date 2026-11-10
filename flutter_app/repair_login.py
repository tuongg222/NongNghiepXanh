from pathlib import Path

p = Path("lib/screens/login_screen.dart")
s = p.read_text()

# Fix biến t chưa khai báo
s = s.replace(
    "(t - .62).clamp(0.0, 1.0)",
    "(introController.value - .62).clamp(0.0, 1.0)"
)

# Thêm ngoặc đóng SafeArea còn thiếu
old = """          ),
        ],
      ),
    );
  }
}"""

new = """          ),
            ),
        ],
      ),
    );
  }
}"""

if old not in s:
    print("KHONG TIM THAY DOAN CUOI FILE")
    raise SystemExit(1)

s = s.replace(old, new, 1)
p.write_text(s)

print("DA SUA opacity va ngoac SafeArea")
