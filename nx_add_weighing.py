from pathlib import Path
from datetime import datetime
import re
import shutil
import sys

p = Path("app/src/main/assets/index.html")
if not p.is_file():
    sys.exit("LỖI: Không tìm thấy index.html.")

s = p.read_text(encoding="utf-8")

# Không chèn trùng khi chạy lại script.
if 'id="weighing"' in s or "nx_weighing_sessions" in s:
    sys.exit("ĐÃ CÓ dấu hiệu tính năng cân bao. Dừng để tránh chèn trùng.")

required = [
    '<button onclick="showPage(\'calc\',this)">⚖️ Tính tiền lúa</button>',
    '<section id="calc" class="page">',
    'function calculate(){',
    'const diseasePhoto = document.getElementById',
    '"nx_cultivation_logs"'
]
for marker in required:
    if marker not in s:
        sys.exit("LỖI: Không tìm thấy vị trí cần sửa: " + marker)

backup = p.with_name(
    p.name + ".before-weighing-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".bak"
)
shutil.copy2(p, backup)

# 1. Menu cân bao nổi bật.
s = s.replace(
    '<button onclick="showPage(\'calc\',this)">⚖️ Tính tiền lúa</button>',
    '<button onclick="showPage(\'weighing\',this);renderWeighing()">⚖️ CÂN TỪNG BAO</button>\n'
    '  <button onclick="showPage(\'calc\',this)">🧮 Tính tiền lúa</button>',
    1
)

# 2. Nút lớn ở trang chủ.
home_anchor = '  <div class="grid">\n'
home_card = """
  <div class="card" style="border:3px solid #218447;background:#f0fff3">
    <h2 style="font-size:25px">⚖️ CÂN TỪNG BAO LÚA</h2>
    <p style="font-size:18px">Nhập cân từng bao, tự cộng kg và tính tiền.</p>
    <button type="button" style="font-size:22px;min-height:64px"
      onclick="showPage('weighing',this);renderWeighing()">BẮT ĐẦU CÂN LÚA</button>
  </div>
"""
s = s.replace(home_anchor, home_card + home_anchor, 1)

# 3. Màn hình cân từng bao.
section_anchor = '<section id="disease" class="page">'
weighing_page = """
<section id="weighing" class="page">
  <div class="card">
    <h2 style="font-size:25px">⚖️ CÂN TỪNG BAO LÚA</h2>
    <p style="font-size:18px">Nhập cân nặng của từng bao. Có thể dùng số lẻ, ví dụ 48,5 kg.</p>

    <label for="nxBagWeight" style="font-size:20px">Cân nặng bao tiếp theo (kg)</label>
    <input id="nxBagWeight" type="text" inputmode="decimal"
      placeholder="Ví dụ: 48,5" autocomplete="off"
      style="font-size:26px;min-height:64px">

    <button type="button" style="font-size:21px;min-height:62px"
      onclick="addWeighingBag()">＋ THÊM BAO NÀY</button>

    <label for="nxBagPrice" style="font-size:20px">Giá mua/bán mỗi kg (đồng)</label>
    <input id="nxBagPrice" type="number" min="0" step="1"
      placeholder="Ví dụ: 8000" style="font-size:22px;min-height:58px"
      oninput="renderWeighing()">

    <label for="nxBagCost" style="font-size:20px">Chi phí (đồng, nếu có)</label>
    <input id="nxBagCost" type="number" min="0" step="1" value="0"
      style="font-size:22px;min-height:58px" oninput="renderWeighing()">

    <div id="nxWeighingSummary" class="result" aria-live="polite"
      style="font-size:20px;line-height:1.9">
      Chưa có bao nào. Hãy nhập cân nặng bao đầu tiên.
    </div>
  </div>

  <div class="card">
    <h2 style="font-size:23px">📋 DANH SÁCH TỪNG BAO</h2>
    <div id="nxWeighingList" style="font-size:18px">Chưa có dữ liệu cân.</div>
    <button type="button" style="font-size:19px;min-height:56px;background:#52665a"
      onclick="finishWeighing()">✓ HOÀN TẤT / XEM TỔNG KẾT</button>
    <button type="button" style="font-size:18px;min-height:52px;background:#a83232"
      onclick="clearWeighing()">XÓA PHIÊN CÂN NÀY</button>
    <small>Mỗi lần thêm bao sẽ được lưu trên điện thoại. Chỉ xóa khi đã chắc chắn.</small>
  </div>
</section>

"""
s = s.replace(section_anchor, weighing_page + section_anchor, 1)

# 4. Hàm xử lý cân; lưu riêng, không đụng dữ liệu giao dịch cũ.
js_anchor = 'const diseasePhoto = document.getElementById'
weighing_js = r"""
// Cân từng bao: lưu cục bộ, kiểm tra dữ liệu và tính lại khi thay đổi.
function getWeighingBags() {
  try {
    const value = JSON.parse(localStorage.getItem("nx_weighing_sessions") || "[]");
    return Array.isArray(value) ? value.filter(function(b) {
      return b && Number.isFinite(Number(b.kg)) && Number(b.kg) > 0;
    }) : [];
  } catch (_) { return []; }
}

function nxWeightNumber(value) {
  let text = String(value == null ? "" : value).trim().replace(/\s/g, "");
  if (!text) return NaN;
  // Cho phép nhập 48,5 hoặc 48.5; không cho nhập nhiều dấu thập phân.
  if (text.includes(",") && text.includes(".")) return NaN;
  text = text.replace(",", ".");
  if (!/^\d+(\.\d{1,3})?$/.test(text)) return NaN;
  return Number(text);
}

function nxWeightMoney(value) {
  const n = Number(value);
  return Number.isFinite(n) && n >= 0 ? n : NaN;
}

function nxFormatNumber(n) {
  return Number(n).toLocaleString("vi-VN", { maximumFractionDigits: 3 });
}

function nxFormatDong(n) {
  return Math.round(n).toLocaleString("vi-VN") + " đồng";
}

function addWeighingBag() {
  const input = document.getElementById("nxBagWeight");
  const kg = nxWeightNumber(input.value);
  if (!Number.isFinite(kg) || kg <= 0 || kg > 1000) {
    alert("Vui lòng nhập cân nặng lớn hơn 0 và không quá 1.000 kg cho mỗi bao. Ví dụ: 48,5");
    input.focus();
    return;
  }

  const bags = getWeighingBags();
  bags.push({ id: Date.now().toString() + "-" + Math.random().toString(36).slice(2, 8), kg: kg });
  try {
    localStorage.setItem("nx_weighing_sessions", JSON.stringify(bags));
  } catch (_) {
    alert("Không lưu được bao cân. Bộ nhớ có thể đã đầy.");
    return;
  }
  input.value = "";
  renderWeighing();
  input.focus();
}

function editWeighingBag(index) {
  const bags = getWeighingBags();
  if (!bags[index]) return;
  const answer = prompt("Nhập cân nặng mới cho bao số " + (index + 1) + " (kg):", String(bags[index].kg).replace(".", ","));
  if (answer === null) return;
  const kg = nxWeightNumber(answer);
  if (!Number.isFinite(kg) || kg <= 0 || kg > 1000) {
    alert("Cân nặng không hợp lệ. Hãy nhập số lớn hơn 0, tối đa 1.000 kg.");
    return;
  }
  bags[index].kg = kg;
  try { localStorage.setItem("nx_weighing_sessions", JSON.stringify(bags)); }
  catch (_) { alert("Không lưu được thay đổi."); return; }
  renderWeighing();
}

function deleteWeighingBag(index) {
  const bags = getWeighingBags();
  if (!bags[index]) return;
  if (!confirm("Xóa bao số " + (index + 1) + " (" + nxFormatNumber(bags[index].kg) + " kg)?")) return;
  bags.splice(index, 1);
  localStorage.setItem("nx_weighing_sessions", JSON.stringify(bags));
  renderWeighing();
}

function renderWeighing() {
  const bags = getWeighingBags();
  const priceInput = document.getElementById("nxBagPrice");
  const costInput = document.getElementById("nxBagCost");
  const summary = document.getElementById("nxWeighingSummary");
  const list = document.getElementById("nxWeighingList");
  if (!summary || !list) return;

  const totalKg = bags.reduce(function(sum, b) { return sum + Number(b.kg); }, 0);
  const price = priceInput && priceInput.value !== "" ? nxWeightMoney(priceInput.value) : NaN;
  const cost = costInput && costInput.value !== "" ? nxWeightMoney(costInput.value) : 0;
  const revenue = Number.isFinite(price) ? Math.round(totalKg * price) : null;
  const profit = revenue === null || !Number.isFinite(cost) ? null : revenue - cost;

  summary.innerHTML =
    '<b>SỐ BAO:</b> ' + bags.length + ' bao<br>' +
    '<b>TỔNG TRỌNG LƯỢNG:</b> <span style="font-size:27px">' + nxFormatNumber(totalKg) + ' kg</span><br>' +
    '<b>GIÁ MỖI KG:</b> ' + (Number.isFinite(price) ? nxFormatDong(price) : "Chưa nhập") + '<br>' +
    '<b>THÀNH TIỀN:</b> <span style="font-size:26px;color:#176b3a">' +
      (revenue === null ? "Nhập giá/kg để tính" : nxFormatDong(revenue)) + '</span><br>' +
    '<b>CHI PHÍ:</b> ' + (Number.isFinite(cost) ? nxFormatDong(cost) : "Giá trị không hợp lệ") + '<br>' +
    '<b>LÃI TẠM TÍNH:</b> <span style="font-size:23px;color:' +
      (profit !== null && profit < 0 ? "#b83232" : "#176b3a") + '">' +
      (profit === null ? "Chưa đủ dữ liệu" : nxFormatDong(profit)) + '</span>';

  if (!bags.length) {
    list.textContent = "Chưa có dữ liệu cân.";
    return;
  }

  list.innerHTML = bags.map(function(b, i) {
    return '<div style="padding:14px 0;border-bottom:2px solid #e3ece2">' +
      '<b style="font-size:21px">Bao số ' + (i + 1) + ': ' + nxFormatNumber(b.kg) + ' kg</b><br>' +
      '<button type="button" style="width:auto;min-width:110px;min-height:48px;background:#245f9e" onclick="editWeighingBag(' + i + ')">SỬA BAO</button> ' +
      '<button type="button" style="width:auto;min-width:110px;min-height:48px;background:#a83232" onclick="deleteWeighingBag(' + i + ')">XÓA BAO</button>' +
      '</div>';
  }).join("");
}

function finishWeighing() {
  const bags = getWeighingBags();
  if (!bags.length) {
    alert("Chưa có bao nào. Hãy nhập cân nặng trước.");
    return;
  }
  renderWeighing();
  const totalKg = bags.reduce(function(sum, b) { return sum + Number(b.kg); }, 0);
  const priceInput = document.getElementById("nxBagPrice");
  const price = priceInput.value === "" ? NaN : nxWeightMoney(priceInput.value);
  if (!Number.isFinite(price)) {
    alert("Đã cân xong " + bags.length + " bao, tổng " + nxFormatNumber(totalKg) + " kg. Hãy nhập giá mỗi kg để tính thành tiền.");
    priceInput.focus();
    return;
  }
  const revenue = Math.round(totalKg * price);
  const costInput = document.getElementById("nxBagCost");
  const cost = costInput.value === "" ? 0 : nxWeightMoney(costInput.value);
  if (!Number.isFinite(cost)) {
    alert("Chi phí không hợp lệ. Vui lòng kiểm tra lại.");
    costInput.focus();
    return;
  }
  alert("HOÀN TẤT CÂN LÚA\n\nSố bao: " + bags.length +
    "\nTổng trọng lượng: " + nxFormatNumber(totalKg) + " kg" +
    "\nGiá mỗi kg: " + nxFormatDong(price) +
    "\nTHÀNH TIỀN: " + nxFormatDong(revenue) +
    "\nChi phí: " + nxFormatDong(cost) +
    "\nLÃI TẠM TÍNH: " + nxFormatDong(revenue - cost));
}

function clearWeighing() {
  const bags = getWeighingBags();
  if (!bags.length) {
    alert("Phiên cân đang trống.");
    return;
  }
  if (!confirm("Xóa toàn bộ " + bags.length + " bao của phiên cân này? Không thể hoàn tác.")) return;
  localStorage.setItem("nx_weighing_sessions", "[]");
  renderWeighing();
}

"""
s = s.replace(js_anchor, weighing_js + js_anchor, 1)

# 5. Thêm khóa vào bộ sao lưu và trình kiểm tra dữ liệu nhập.
s = s.replace(
    '"nx_cultivation_logs"\n];',
    '"nx_cultivation_logs", "nx_weighing_sessions"\n];',
    1
)
s = s.replace(
    'nx_cultivation_logs: Array.isArray',
    'nx_cultivation_logs: Array.isArray,\n      nx_weighing_sessions: Array.isArray',
    1
)
s = s.replace(
    'if (typeof renderCultivationLogs === "function") renderCultivationLogs();',
    'if (typeof renderCultivationLogs === "function") renderCultivationLogs();\n'
    '      if (typeof renderWeighing === "function") renderWeighing();',
    1
)

# Ghi tệp một lần sau khi tất cả vị trí đã được xử lý.
p.write_text(s, encoding="utf-8")
print("ĐÃ TÍCH HỢP CÂN TỪNG BAO.")
print("Bản sao lưu:", backup)
