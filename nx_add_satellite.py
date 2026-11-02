from pathlib import Path
from datetime import datetime

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")

old = """  const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19, subdomains: 'abc',
    attribution: '&copy; OpenStreetMap contributors',
    crossOrigin: true
  }).addTo(farmMapInstance);
  let tileErrorShown = false;
  tileLayer.on('tileerror', function(){
    if (tileErrorShown) return;
    tileErrorShown = true;
    const note = document.getElementById('farmMapNotice');
    if (note) note.textContent = 'Không tải được ảnh bản đồ. Hãy kiểm tra Internet hoặc tắt VPN/chặn quảng cáo rồi mở lại. Bạn vẫn có thể thử đo sau khi bản đồ hiện.';
  });
  tileLayer.on('tileload', function(){
    const note = document.getElementById('farmMapNotice');
    if (note) note.textContent = 'Chạm lần lượt ít nhất 3 góc ruộng trên bản đồ để tính diện tích.';
  });"""

new = """  const streetLayer = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    {
      maxZoom: 19,
      subdomains: 'abc',
      attribution: '&copy; OpenStreetMap contributors'
    }
  );

  const satelliteLayer = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    {
      maxZoom: 19,
      attribution: 'Imagery &copy; Esri and its imagery providers'
    }
  );

  streetLayer.addTo(farmMapInstance);

  L.control.layers(
    {
      'Bản đồ thường': streetLayer,
      'Vệ tinh': satelliteLayer
    },
    null,
    { collapsed: false }
  ).addTo(farmMapInstance);

  function setMapNotice(message) {
    const note = document.getElementById('farmMapNotice');
    if (note) note.textContent = message;
  }

  let tileErrorShown = false;
  [streetLayer, satelliteLayer].forEach(function(layer) {
    layer.on('tileerror', function() {
      if (layer !== farmMapInstance._layers[Object.keys(farmMapInstance._layers).find(
        function(k) { return farmMapInstance._layers[k] === layer; }
      )]) return;
      if (tileErrorShown) return;
      tileErrorShown = true;
      setMapNotice(
        'Không tải được ảnh bản đồ. Hãy kiểm tra Internet, VPN hoặc bộ lọc mạng rồi thử lại.'
      );
    });

    layer.on('tileload', function() {
      tileErrorShown = false;
      setMapNotice(
        'Chọn lớp Vệ tinh hoặc Bản đồ thường. Chạm ít nhất 3 góc ruộng để tính diện tích.'
      );
    });
  });"""

if s.count(old) != 1:
    print("DUNG: Không tìm thấy duy nhất đoạn khởi tạo bản đồ cũ.")
    print("Số đoạn khớp:", s.count(old))
    print("Chưa sửa tệp.")
    raise SystemExit(1)

backup = p.with_name(
    p.name + ".before-satellite-" + datetime.now().strftime("%Y%m%d-%H%M%S") + ".bak"
)
backup.write_text(s, encoding="utf-8")
p.write_text(s.replace(old, new, 1), encoding="utf-8")

print("Đã sao lưu:", backup)
print("Đã thêm lớp Bản đồ thường / Vệ tinh.")
print("Chưa biên dịch APK; cần kiểm tra mã trước.")
