from pathlib import Path
from datetime import datetime

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")

if 'id="business"' in s:
    print("Trang kinh doanh da ton tai; khong chen trung.")
    raise SystemExit(0)

nav = '  <button onclick="showPage(\'finance\',this)">💰 Sổ thu chi</button>'
if nav not in s:
    raise SystemExit("Khong tim thay nut So thu chi trong menu.")

section = '<footer>Nông Nghiệp Xanh · Phiên bản thử nghiệm 1.0</footer>'
if section not in s:
    raise SystemExit("Khong tim thay footer.")

js_anchor = 'function showPage(id,btn){'
if js_anchor not in s:
    raise SystemExit("Khong tim thay ham showPage.")

backup = p.with_name(
    p.name + ".before-business-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".bak"
)
backup.write_text(s, encoding="utf-8")

new_nav = nav + '''
  <button onclick="showPage('business',this);calculateBusiness()">📊 Thị trường & Kinh doanh</button>'''

new_section = r'''
<section id="business" class="page">
  <div class="card">
    <h2>📊 Phân tích thị trường & Kinh doanh</h2>
    <p>Điều chỉnh các giả định để lập kế hoạch kinh doanh ứng dụng.</p>
    <div class="result">
      <b>Quy mô tham khảo:</b> khoảng 8,01 triệu hộ nông thôn có ngành sản xuất chính là nông, lâm nghiệp và thủy sản theo thống kê năm 2025.
      <br><small>Đây là số hộ, không phải số người dùng ứng dụng. Hãy xác minh nguồn thống kê trước khi dùng trong hồ sơ kinh doanh.</small>
    </div>

    <h3>🎯 Thị trường và người dùng</h3>
    <label>Quy mô thị trường mục tiêu (hộ/người, ước tính)</label>
    <input id="bizMarket" type="number" min="0" value="100000" oninput="calculateBusiness()">
    <label>Người dùng giai đoạn 1</label>
    <input id="bizUsers1" type="number" min="0" value="500" oninput="calculateBusiness()">
    <label>Người dùng giai đoạn 2 (lũy kế)</label>
    <input id="bizUsers2" type="number" min="0" value="3000" oninput="calculateBusiness()">

    <h3>💳 Doanh thu</h3>
    <label>Tỷ lệ người dùng trả phí (%)</label>
    <input id="bizConversion" type="number" min="0" max="100" step="0.1" value="10" oninput="calculateBusiness()">
    <label>Giá thuê bao mỗi tháng (đồng)</label>
    <input id="bizPrice" type="number" min="0" step="1000" value="29000" oninput="calculateBusiness()">

    <h3>🧾 Chi phí</h3>
    <label>Chi phí khởi tạo (đồng)</label>
    <input id="bizSetup" type="number" min="0" step="100000" value="20000000" oninput="calculateBusiness()">
    <label>Chi phí mỗi tháng giai đoạn 1 (đồng)</label>
    <input id="bizCost1" type="number" min="0" step="100000" value="5000000" oninput="calculateBusiness()">
    <label>Chi phí mỗi tháng giai đoạn 2 (đồng)</label>
    <input id="bizCost2" type="number" min="0" step="100000" value="20000000" oninput="calculateBusiness()">

    <button onclick="saveBusinessPlan()">💾 Lưu giả định</button>
    <button onclick="resetBusinessPlan()" style="background:#64748b">Khôi phục số mẫu</button>
    <small>Số mặc định chỉ để minh họa, không phải số liệu kinh doanh thực tế.</small>
  </div>

  <div class="card">
    <h2>📈 Kết quả dự kiến</h2>
    <div class="grid">
      <div class="tile"><b>Giai đoạn 1</b><div id="bizSummary1">—</div></div>
      <div class="tile"><b>Giai đoạn 2</b><div id="bizSummary2">—</div></div>
    </div>
    <div id="bizResults" class="result" aria-live="polite"></div>
    <h3>So sánh doanh thu và chi phí mỗi tháng</h3>
    <div id="bizBars"></div>
    <h3>Điểm hòa vốn</h3>
    <div id="bizBreakEven" class="result"></div>
    <small>Kết quả chưa tính thuế, phí thanh toán và các khoản chưa nhập.</small>
  </div>

  <div class="card">
    <h2>🔎 Ba kịch bản phát triển</h2>
    <div id="bizScenarios"></div>
  </div>
</section>
'''

business_js = r'''
const bizDefaults = {
  bizMarket:100000, bizUsers1:500, bizUsers2:3000,
  bizConversion:10, bizPrice:29000, bizSetup:20000000,
  bizCost1:5000000, bizCost2:20000000
};
const bizIds = Object.keys(bizDefaults);
function bizNum(id) {
  const el = document.getElementById(id);
  const n = el ? Number(el.value) : 0;
  return Number.isFinite(n) ? Math.max(0,n) : 0;
}
function bizMoney(n) {
  return Math.round(n).toLocaleString('vi-VN') + ' đ';
}
function saveBusinessPlan() {
  const data = {};
  bizIds.forEach(id => data[id] = bizNum(id));
  try {
    localStorage.setItem('nx_business_plan',JSON.stringify(data));
    alert('Đã lưu giả định trên thiết bị này.');
  } catch(e) {
    alert('Không lưu được dữ liệu. Hãy kiểm tra bộ nhớ thiết bị.');
  }
  calculateBusiness();
}
function resetBusinessPlan() {
  bizIds.forEach(id => document.getElementById(id).value = bizDefaults[id]);
  try { localStorage.removeItem('nx_business_plan'); } catch(e) {}
  calculateBusiness();
}
function loadBusinessPlan() {
  try {
    const data = JSON.parse(localStorage.getItem('nx_business_plan') || 'null');
    if (data) bizIds.forEach(id => {
      if (data[id] !== undefined && Number.isFinite(Number(data[id])))
        document.getElementById(id).value = Math.max(0,Number(data[id]));
    });
  } catch(e) {}
}
function calculateBusiness() {
  const el = id => document.getElementById(id);
  if (!el('bizResults')) return;
  const market = bizNum('bizMarket');
  const u1 = bizNum('bizUsers1'), u2 = bizNum('bizUsers2');
  const rate = Math.min(100,bizNum('bizConversion'))/100;
  const price = bizNum('bizPrice'), setup = bizNum('bizSetup');
  const c1 = bizNum('bizCost1'), c2 = bizNum('bizCost2');
  const paid1 = Math.floor(u1*rate), paid2 = Math.floor(u2*rate);
  const r1 = paid1*price, r2 = paid2*price;
  const p1 = r1-c1, p2 = r2-c2;
  const total1 = p1*6-setup, total2 = p2*12;
  el('bizSummary1').textContent = u1.toLocaleString('vi-VN')+' người dùng; '+paid1.toLocaleString('vi-VN')+' trả phí';
  el('bizSummary2').textContent = u2.toLocaleString('vi-VN')+' người dùng; '+paid2.toLocaleString('vi-VN')+' trả phí';
  el('bizResults').innerHTML =
    '<b>Giai đoạn 1 — 6 tháng</b><br>Doanh thu/tháng: '+bizMoney(r1)+
    '<br>Lãi/lỗ vận hành/tháng: '+bizMoney(p1)+
    '<br>Lãi/lỗ 6 tháng sau chi phí khởi tạo: <b>'+bizMoney(total1)+'</b><hr>'+
    '<b>Giai đoạn 2 — 12 tháng tiếp theo</b><br>Doanh thu/tháng: '+bizMoney(r2)+
    '<br>Lãi/lỗ vận hành/tháng: '+bizMoney(p2)+
    '<br>Lãi/lỗ 12 tháng: <b>'+bizMoney(total2)+'</b><hr>'+
    'Tỷ lệ tiếp cận thị trường mục tiêu: '+
    (market ? (u2/market*100).toLocaleString('vi-VN',{maximumFractionDigits:2})+'%' : 'Chưa xác định');
  function bar(name,rev,cost) {
    const max = Math.max(rev,cost,1);
    return '<div style="margin:12px 0"><b>'+name+'</b>'+
      '<p>Doanh thu: '+bizMoney(rev)+'</p>'+
      '<div style="height:12px;background:#e5e7eb;border-radius:8px;overflow:hidden"><div style="height:12px;width:'+Math.min(100,rev/max*100)+'%;background:#16a34a"></div></div>'+
      '<p>Chi phí: '+bizMoney(cost)+'</p>'+
      '<div style="height:12px;background:#e5e7eb;border-radius:8px;overflow:hidden"><div style="height:12px;width:'+Math.min(100,cost/max*100)+'%;background:#ea580c"></div></div></div>';
  }
  el('bizBars').innerHTML = bar('Giai đoạn 1',r1,c1)+bar('Giai đoạn 2',r2,c2);
  const perUser = price*rate;
  el('bizBreakEven').textContent = perUser>0 ?
    'Cần khoảng '+Math.ceil(c2/perUser).toLocaleString('vi-VN')+
    ' người dùng tổng cộng để bù chi phí vận hành tháng giai đoạn 2, theo tỷ lệ trả phí hiện tại; chưa tính chi phí khởi tạo.' :
    'Chưa tính được: giá thuê bao và tỷ lệ trả phí phải lớn hơn 0.';
  const scenarios = [
    {name:'Thận trọng',f:0.5,c:1.2},
    {name:'Cơ sở',f:1,c:1},
    {name:'Tăng trưởng cao',f:2,c:1.5}
  ];
  el('bizScenarios').innerHTML = scenarios.map(sc=>{
    const users=Math.floor(u2*sc.f), paid=Math.floor(users*rate);
    const rev=paid*price, cost=c2*sc.c;
    return '<div style="padding:10px 0;border-bottom:1px solid #ddd"><b>'+sc.name+
      '</b><br>Người dùng: '+users.toLocaleString('vi-VN')+
      '<br>Người trả phí: '+paid.toLocaleString('vi-VN')+
      '<br>Doanh thu/tháng: '+bizMoney(rev)+
      '<br>Chi phí/tháng: '+bizMoney(cost)+
      '<br>Lãi/lỗ/tháng: <b>'+bizMoney(rev-cost)+'</b></div>';
  }).join('');
}
'''

s = s.replace(nav, new_nav, 1)
s = s.replace(section, new_section + "\n" + section, 1)
s = s.replace(js_anchor, business_js + "\n" + js_anchor, 1)

# Nạp lại giả định đã lưu khi mở trang.
end_script = '</script>'
if end_script not in s:
    raise SystemExit("Khong tim thay the dong script.")
s = s.replace(end_script, '\nloadBusinessPlan();\ncalculateBusiness();\n' + end_script, 1)

p.write_text(s, encoding="utf-8")
print("Da them trang Phan tich thi truong & Kinh doanh.")
print("Ban sao luu:", backup)
