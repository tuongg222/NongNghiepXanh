from pathlib import Path
from datetime import datetime
import re
import sys

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")

if 'id="backup"' in s or "function exportNxBackup()" in s:
    sys.exit("DỪNG: Tính năng sao lưu có vẻ đã tồn tại.")

nav_anchor = "</nav>"
page_anchor = '<section id="business"'
js_anchor = "loadFarm();renderTaskFarmOptions();renderTasks();syncAllCareReminders();"

for name, anchor in [
    ("menu", nav_anchor),
    ("trang kinh doanh", page_anchor),
    ("khởi tạo JavaScript", js_anchor),
]:
    n = s.count(anchor)
    print(f"{name}: {n} vị trí")
    if n != 1:
        sys.exit("DỪNG: Không sửa index.html vì vị trí chèn chưa chắc chắn.")

nav = '''
<button type="button" onclick="showPage('backup',this)">Sao lưu dữ liệu</button>
'''

page = r'''
<section id="backup" class="page">
  <div class="card">
    <h2>Sao lưu dữ liệu</h2>
    <p>Xuất dữ liệu đang lưu trên điện thoại thành tệp JSON.</p>
    <p>Hãy giữ tệp sao lưu ở nơi an toàn vì nó có thể chứa thông tin canh tác và thu chi.</p>
    <button type="button" onclick="exportNxBackup()">Xuất bản sao lưu</button>
  </div>
  <div class="card">
    <h2>Khôi phục dữ liệu</h2>
    <p>Chọn tệp JSON đã xuất từ ứng dụng. Nên sao lưu dữ liệu hiện tại trước khi khôi phục.</p>
    <input id="nxBackupFile" type="file" accept=".json,application/json">
    <button type="button" onclick="importNxBackup()">Khôi phục dữ liệu</button>
    <p id="nxBackupStatus" role="status" aria-live="polite"></p>
  </div>
</section>
'''

js = r'''
const NX_BACKUP_KEYS = [
  "nx_farms", "nx_farm", "nx_tasks", "nx_transactions",
  "nx_disease_photos", "nx_weather_daily", "nx_business_plan"
];

function exportNxBackup() {
  const status = document.getElementById("nxBackupStatus");
  try {
    const data = {};
    NX_BACKUP_KEYS.forEach(function(key) {
      const raw = localStorage.getItem(key);
      if (raw !== null) data[key] = JSON.parse(raw);
    });
    const payload = {
      app: "NongNghiepXanh",
      schemaVersion: 1,
      exportedAt: new Date().toISOString(),
      data: data
    };
    const blob = new Blob([JSON.stringify(payload, null, 2)], {
      type: "application/json;charset=utf-8"
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "NongNghiepXanh-backup-" +
      new Date().toISOString().slice(0, 10) + ".json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function() { URL.revokeObjectURL(url); }, 1500);
    status.textContent = "Đã yêu cầu xuất tệp. Kiểm tra thư mục Tải xuống.";
  } catch (e) {
    status.textContent = "Xuất thất bại: " + e.message;
  }
}

function importNxBackup() {
  const input = document.getElementById("nxBackupFile");
  const status = document.getElementById("nxBackupStatus");
  const file = input && input.files && input.files[0];

  if (!file) {
    status.textContent = "Hãy chọn tệp JSON trước.";
    return;
  }
  if (file.size <= 0 || file.size > 25 * 1024 * 1024) {
    status.textContent = "Tệp phải lớn hơn 0 và không quá 25 MB.";
    return;
  }

  const reader = new FileReader();
  reader.onerror = function() {
    status.textContent = "Không đọc được tệp.";
  };
  reader.onload = function() {
    let payload;
    try {
      payload = JSON.parse(String(reader.result || ""));
    } catch (_) {
      status.textContent = "Tệp JSON không hợp lệ.";
      return;
    }

    if (!payload || payload.app !== "NongNghiepXanh" ||
        payload.schemaVersion !== 1 || !payload.data ||
        typeof payload.data !== "object" || Array.isArray(payload.data)) {
      status.textContent = "Tệp không đúng định dạng sao lưu.";
      return;
    }

    const validators = {
      nx_farms: Array.isArray,
      nx_farm: function(v) {
        return v !== null && typeof v === "object" && !Array.isArray(v);
      },
      nx_tasks: Array.isArray,
      nx_transactions: Array.isArray,
      nx_disease_photos: Array.isArray,
      nx_weather_daily: Array.isArray,
      nx_business_plan: function(v) {
        return v !== null && typeof v === "object" && !Array.isArray(v);
      }
    };
    const keys = Object.keys(payload.data);
    if (!keys.length || keys.some(function(k) {
      return !NX_BACKUP_KEYS.includes(k);
    })) {
      status.textContent = "Tệp trống hoặc chứa khóa không được hỗ trợ.";
      return;
    }

    const serialized = {};
    try {
      keys.forEach(function(k) {
        if (!validators[k](payload.data[k])) {
          throw new Error("Dữ liệu sai định dạng: " + k);
        }
        serialized[k] = JSON.stringify(payload.data[k]);
      });
    } catch (e) {
      status.textContent = e.message || "Không thể kiểm tra dữ liệu.";
      return;
    }

    if (!confirm("Khôi phục sẽ thay thế các nhóm dữ liệu có trong tệp. " +
        "Bạn đã sao lưu dữ liệu hiện tại và muốn tiếp tục chưa?")) {
      status.textContent = "Đã hủy khôi phục.";
      return;
    }

    const previous = {};
    NX_BACKUP_KEYS.forEach(function(k) {
      previous[k] = localStorage.getItem(k);
    });

    try {
      keys.forEach(function(k) {
        localStorage.setItem(k, serialized[k]);
      });
    } catch (e) {
      NX_BACKUP_KEYS.forEach(function(k) {
        try {
          if (previous[k] === null) localStorage.removeItem(k);
          else localStorage.setItem(k, previous[k]);
        } catch (_) {}
      });
      status.textContent = "Ghi dữ liệu thất bại; đã thử hoàn tác. " + e.message;
      return;
    }

    try {
      if (typeof renderFarms === "function") renderFarms();
      if (typeof renderTaskFarmOptions === "function") renderTaskFarmOptions();
      if (typeof renderTasks === "function") renderTasks();
      if (typeof renderTransactions === "function") renderTransactions();
      if (typeof loadDiseasePhotos === "function") loadDiseasePhotos();
      if (typeof syncAllCareReminders === "function") syncAllCareReminders();
      status.textContent = "Đã nhập dữ liệu. Hãy kiểm tra các danh sách.";
      input.value = "";
    } catch (e) {
      status.textContent = "Đã nhập dữ liệu nhưng giao diện chưa làm mới được. " +
        "Hãy mở lại ứng dụng. " + e.message;
    }
  };
  reader.readAsText(file);
}
'''

# Xác minh các hàm làm mới được gọi trong ứng dụng hiện tại.
for fn in ["renderFarms", "renderTaskFarmOptions", "renderTasks",
           "renderTransactions", "syncAllCareReminders"]:
    if not re.search(r"\bfunction\s+" + re.escape(fn) + r"\s*\(", s):
        sys.exit("DỪNG: Không tìm thấy định nghĩa hàm " + fn)

updated = s.replace(nav_anchor, nav + "\n" + nav_anchor, 1)
updated = updated.replace(page_anchor, page + "\n" + page_anchor, 1)
updated = updated.replace(js_anchor, js + "\n" + js_anchor, 1)

stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
backup = p.with_name(p.name + ".before-backup-" + stamp + ".bak")
backup.write_text(s, encoding="utf-8")
p.write_text(updated, encoding="utf-8")

print("Đã sao lưu bản gốc:", backup)
print("Đã cập nhật:", p)
