from pathlib import Path
from datetime import datetime
import shutil
import re
import sys

p = Path("app/src/main/assets/index.html")
if not p.is_file():
    sys.exit("LỖI: Không tìm thấy " + str(p))

s = p.read_text(encoding="utf-8")

# Không chạy lại trên tệp đã tích hợp.
if 'id="cultivationJournal"' in s or "function saveCultivationLog()" in s:
    sys.exit("Đã phát hiện Nhật ký canh tác. Dừng để tránh chèn trùng.")

required = [
    '<nav>',
    '<button type="button" onclick="showPage(\'backup\',this)">Sao lưu dữ liệu</button>',
    '<section id="backup" class="page">',
    'const NX_BACKUP_KEYS = [',
    'const validators = {',
    'status.textContent = "Đã nhập dữ liệu. Hãy kiểm tra các danh sách.";'
]
for anchor in required:
    if anchor not in s:
        sys.exit("LỖI: Không tìm thấy vị trí cần sửa: " + repr(anchor))

backup = p.with_name(
    p.name + ".before-journal-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".bak"
)
shutil.copy2(p, backup)
original = s

# 1. Thêm nút điều hướng.
s = s.replace(
    '<button type="button" onclick="showPage(\'backup\',this)">Sao lưu dữ liệu</button>',
    '<button type="button" onclick="showPage(\'cultivationJournal\',this);renderCultivationLogs()">📓 Nhật ký canh tác</button>\n'
    '<button type="button" onclick="showPage(\'backup\',this)">Sao lưu dữ liệu</button>',
    1
)

# 2. Thêm trang nhật ký trước trang sao lưu.
journal_page = r'''
<section id="cultivationJournal" class="page">
  <div class="card">
    <h2>📓 Nhật ký canh tác</h2>
    <p>Ghi lại hoạt động, vật tư và chi phí theo từng ruộng.</p>
    <input id="cultivationLogId" type="hidden">
    <label>Ruộng lúa</label>
    <select id="cultivationLogFarm">
      <option value="">Chưa gắn ruộng</option>
    </select>
    <label>Ngày thực hiện</label>
    <input id="cultivationLogDate" type="date">
    <label>Hoạt động</label>
    <select id="cultivationLogType">
      <option>Chuẩn bị đất</option>
      <option>Gieo sạ</option>
      <option>Bón phân</option>
      <option>Phun thuốc</option>
      <option>Kiểm tra sâu bệnh</option>
      <option>Tưới / quản lý nước</option>
      <option>Làm cỏ</option>
      <option>Thu hoạch</option>
      <option>Khác</option>
    </select>
    <label>Vật tư sử dụng</label>
    <input id="cultivationLogMaterial" maxlength="200"
           placeholder="Ví dụ: Phân NPK, số lượng">
    <label>Chi phí (đồng)</label>
    <input id="cultivationLogCost" type="number" min="0" step="1000"
           placeholder="0">
    <label>Ghi chú công việc</label>
    <textarea id="cultivationLogNotes" maxlength="3000" rows="4"
              placeholder="Tình trạng ruộng, kết quả, lưu ý..."></textarea>
    <button type="button" onclick="saveCultivationLog()">💾 Lưu nhật ký</button>
    <button type="button" onclick="resetCultivationLog()"
            style="background:#607568">Hủy sửa / làm mới biểu mẫu</button>
    <p id="cultivationLogStatus" role="status" aria-live="polite"></p>
  </div>
  <div class="card">
    <h2>📚 Nhật ký đã ghi</h2>
    <label>Lọc theo ruộng</label>
    <select id="cultivationLogFilter" onchange="renderCultivationLogs()">
      <option value="">Tất cả ruộng</option>
    </select>
    <div id="cultivationLogList">Chưa có nhật ký.</div>
  </div>
</section>

'''
s = s.replace(
    '<section id="backup" class="page">',
    journal_page + '<section id="backup" class="page">',
    1
)

# 3. Thêm chức năng quản lý nhật ký trước cấu hình backup.
journal_js = r'''
// Nhật ký canh tác: lưu cục bộ, độc lập với dữ liệu đăng nhập.
function getCultivationLogs() {
  try {
    const value = JSON.parse(localStorage.getItem("nx_cultivation_logs") || "[]");
    return Array.isArray(value) ? value.filter(function(item) {
      return item && typeof item === "object" && !Array.isArray(item);
    }) : [];
  } catch (_) {
    return [];
  }
}

function renderCultivationFarmOptions() {
  const farms = getFarms();
  const farmSelect = document.getElementById("cultivationLogFarm");
  const filter = document.getElementById("cultivationLogFilter");
  if (!farmSelect || !filter) return;

  const oldFarm = farmSelect.value;
  const oldFilter = filter.value;
  const options = farms.map(function(farm) {
    return '<option value="' + Number(farm.id) + '">' +
      esc(farm.name || "Ruộng chưa đặt tên") + '</option>';
  }).join("");

  farmSelect.innerHTML = '<option value="">Chưa gắn ruộng</option>' + options;
  filter.innerHTML = '<option value="">Tất cả ruộng</option>' + options;

  if (Array.from(farmSelect.options).some(function(o) { return o.value === oldFarm; })) {
    farmSelect.value = oldFarm;
  }
  if (Array.from(filter.options).some(function(o) { return o.value === oldFilter; })) {
    filter.value = oldFilter;
  }
}

function resetCultivationLog() {
  document.getElementById("cultivationLogId").value = "";
  document.getElementById("cultivationLogDate").value =
    new Date().toLocaleDateString("sv-SE");
  document.getElementById("cultivationLogType").selectedIndex = 0;
  document.getElementById("cultivationLogMaterial").value = "";
  document.getElementById("cultivationLogCost").value = "";
  document.getElementById("cultivationLogNotes").value = "";
  document.getElementById("cultivationLogStatus").textContent = "";
}

function saveCultivationLog() {
  const status = document.getElementById("cultivationLogStatus");
  const date = document.getElementById("cultivationLogDate").value;
  const type = document.getElementById("cultivationLogType").value;
  const farmValue = document.getElementById("cultivationLogFarm").value;
  const material = document.getElementById("cultivationLogMaterial").value.trim();
  const notes = document.getElementById("cultivationLogNotes").value.trim();
  const costInput = document.getElementById("cultivationLogCost").value;
  const cost = costInput === "" ? 0 : Number(costInput);
  const idInput = document.getElementById("cultivationLogId").value;

  if (!date || !type) {
    status.textContent = "Hãy chọn ngày và hoạt động.";
    return;
  }
  if (!Number.isFinite(cost) || cost < 0 || cost > Number.MAX_SAFE_INTEGER) {
    status.textContent = "Chi phí không hợp lệ.";
    return;
  }

  const farms = getFarms();
  const farm = farmValue ? farms.find(function(f) {
    return String(f.id) === farmValue;
  }) : null;
  if (farmValue && !farm) {
    status.textContent = "Ruộng đã chọn không còn tồn tại. Hãy chọn lại.";
    return;
  }

  const logs = getCultivationLogs();
  const entry = {
    id: idInput || ("journal_" + Date.now() + "_" +
      Math.random().toString(36).slice(2)),
    farmId: farm ? farm.id : null,
    farmName: farm ? String(farm.name || "") : "",
    date: date,
    type: type,
    material: material,
    cost: cost,
    notes: notes,
    updatedAt: new Date().toISOString()
  };

  const index = idInput ? logs.findIndex(function(x) {
    return String(x.id) === idInput;
  }) : -1;

  if (idInput && index < 0) {
    status.textContent = "Không tìm thấy nhật ký cần sửa. Hãy tải lại danh sách.";
    return;
  }
  if (index >= 0) logs[index] = entry;
  else logs.push(entry);

  try {
    localStorage.setItem("nx_cultivation_logs", JSON.stringify(logs));
  } catch (error) {
    status.textContent = "Không lưu được nhật ký: " + error.message;
    return;
  }

  resetCultivationLog();
  status.textContent = index >= 0 ? "Đã cập nhật nhật ký." : "Đã lưu nhật ký.";
  renderCultivationLogs();
}

function editCultivationLog(id) {
  const log = getCultivationLogs().find(function(x) {
    return String(x.id) === String(id);
  });
  if (!log) return;

  renderCultivationFarmOptions();
  document.getElementById("cultivationLogId").value = String(log.id);
  document.getElementById("cultivationLogFarm").value =
    log.farmId == null ? "" : String(log.farmId);
  document.getElementById("cultivationLogDate").value = log.date || "";
  document.getElementById("cultivationLogType").value = log.type || "Khác";
  document.getElementById("cultivationLogMaterial").value = log.material || "";
  document.getElementById("cultivationLogCost").value = log.cost || "";
  document.getElementById("cultivationLogNotes").value = log.notes || "";
  document.getElementById("cultivationLogStatus").textContent =
    "Đang sửa nhật ký. Nhấn Lưu nhật ký để xác nhận.";
  document.getElementById("cultivationJournal").scrollIntoView({behavior:"smooth"});
}

function deleteCultivationLog(id) {
  if (!confirm("Bạn có chắc muốn xóa nhật ký này không?")) return;
  const logs = getCultivationLogs();
  const next = logs.filter(function(x) {
    return String(x.id) !== String(id);
  });
  try {
    localStorage.setItem("nx_cultivation_logs", JSON.stringify(next));
  } catch (error) {
    alert("Không xóa được nhật ký: " + error.message);
    return;
  }
  renderCultivationLogs();
}

function renderCultivationLogs() {
  renderCultivationFarmOptions();
  const list = document.getElementById("cultivationLogList");
  const filter = document.getElementById("cultivationLogFilter");
  if (!list || !filter) return;

  const selected = filter.value;
  const logs = getCultivationLogs().filter(function(log) {
    return !selected || String(log.farmId) === selected;
  }).sort(function(a, b) {
    return String(b.date || "").localeCompare(String(a.date || ""));
  });

  if (!logs.length) {
    list.textContent = "Chưa có nhật ký phù hợp.";
    return;
  }

  list.innerHTML = logs.map(function(log) {
    const id = JSON.stringify(String(log.id));
    return '<div style="padding:12px 0;border-bottom:1px solid #eee">' +
      '<b>' + esc(log.date || "Chưa có ngày") + " · " +
      esc(log.type || "Hoạt động") + '</b><br>' +
      '<small>🌾 ' + esc(log.farmName || "Chưa gắn ruộng") +
      ' · Chi phí: ' + Number(log.cost || 0).toLocaleString("vi-VN") + ' đ</small>' +
      (log.material ? '<p>🧪 Vật tư: ' + esc(log.material) + '</p>' : '') +
      (log.notes ? '<p style="white-space:pre-wrap">' + esc(log.notes) + '</p>' : '') +
      '<button type="button" style="width:auto;padding:7px 12px" ' +
      'onclick="editCultivationLog(' + id + ')">Sửa</button> ' +
      '<button type="button" style="width:auto;padding:7px 12px;background:#b83232" ' +
      'onclick="deleteCultivationLog(' + id + ')">Xóa</button></div>';
  }).join("");
}

'''
s = s.replace("const NX_BACKUP_KEYS = [", journal_js + "const NX_BACKUP_KEYS = [", 1)

# 4. Thêm khóa vào danh sách sao lưu.
s = s.replace(
    '"nx_disease_photos", "nx_weather_daily", "nx_business_plan"',
    '"nx_disease_photos", "nx_weather_daily", "nx_business_plan",\n  "nx_cultivation_logs"',
    1
)

# 5. Kiểm tra cấu trúc mảng validators rồi thêm validator.
validator_anchor = '''      nx_business_plan: function(v) {
        return v !== null && typeof v === "object" && !Array.isArray(v);
      }
'''
if validator_anchor not in s:
    shutil.copy2(backup, p)
    sys.exit("LỖI: Không khớp cấu trúc validators; đã phục hồi bản gốc.")

s = s.replace(
    validator_anchor,
    validator_anchor.rstrip() + ''',
      nx_cultivation_logs: Array.isArray
''',
    1
)

# 6. Làm mới danh sách nhật ký sau khi nhập bản sao lưu.
refresh_anchor = '      if (typeof renderTransactions === "function") renderTransactions();'
if refresh_anchor not in s:
    shutil.copy2(backup, p)
    sys.exit("LỖI: Không tìm thấy vị trí làm mới sau nhập backup.")

s = s.replace(
    refresh_anchor,
    refresh_anchor + '\n      if (typeof renderCultivationLogs === "function") renderCultivationLogs();',
    1
)

# Đảm bảo mọi bước thay thế có hiệu lực và không sửa ngoài ý muốn.
checks = [
    'id="cultivationJournal"',
    "function saveCultivationLog()",
    "function renderCultivationLogs()",
    '"nx_cultivation_logs"',
    "nx_cultivation_logs: Array.isArray"
]
if any(x not in s for x in checks):
    shutil.copy2(backup, p)
    sys.exit("LỖI: Kiểm tra sau sửa không đạt; đã phục hồi bản gốc.")

p.write_text(s, encoding="utf-8")
print("ĐÃ TÍCH HỢP NHẬT KÝ CANH TÁC.")
print("Bản sao lưu:", backup)
print("Tệp đã sửa:", p)
