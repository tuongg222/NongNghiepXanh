
function showPage(id,btn){
 document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
 document.getElementById(id).classList.add('active');
 document.querySelectorAll('nav button').forEach(b=>b.classList.remove('active'));
 btn.classList.add('active');
}
function getFarms(){
 try {
  const saved = JSON.parse(localStorage.getItem('nx_farms') || 'null');
  if (Array.isArray(saved)) return saved;
  const old = JSON.parse(localStorage.getItem('nx_farm') || 'null');
  if (old && typeof old === 'object') {
   const migrated = [{...old, id: Date.now()}];
   localStorage.setItem('nx_farms', JSON.stringify(migrated));
   return migrated;
  }
  return [];
 } catch (error) {
  alert('Không đọc được dữ liệu ruộng. Dữ liệu cũ vẫn được giữ nguyên.');
  return [];
 }
}
let editingFarmId = null;

function saveFarm(){
 const data = {
  name: fieldName.value.trim(),
  variety: variety.value.trim(),
  area: area.value,
  sowDate: sowDate.value
 };
 if (!data.name) {
  alert('Bạn hãy nhập tên ruộng nhé.');
  fieldName.focus();
  return;
 }
 if (data.area !== '' && (!Number.isFinite(Number(data.area)) || Number(data.area) <= 0)) {
  alert('Diện tích phải lớn hơn 0.');
  area.focus();
  return;
 }
 const farms = getFarms();
 if (editingFarmId !== null) {
  const index = farms.findIndex(f => f.id === editingFarmId);
  if (index < 0) {
   alert('Không tìm thấy ruộng cần sửa. Vui lòng tải lại danh sách.');
   return;
  }
  farms[index] = {...farms[index], ...data};
 } else {
  data.id = Date.now();
  farms.push(data);
 }
 try {
  localStorage.setItem('nx_farms', JSON.stringify(farms));
 } catch (error) {
  alert('Không lưu được. Bộ nhớ có thể đã đầy.');
  return;
 }
 editingFarmId = null;
 fieldName.value = '';
 variety.value = '';
 area.value = '';
 sowDate.value = '';
 farmResult.style.display = 'block';
 farmResult.textContent = 'Đã lưu thông tin ruộng!';
 const saveButton = document.querySelector('#farm button');
 if (saveButton) saveButton.textContent = 'Lưu thông tin ruộng';
 renderFarms();
}

function renderFarms(){
 const list = document.getElementById('farmList');
 if (!list) return;
 const farms = getFarms();
 if (!farms.length) {
  list.textContent = 'Chưa có ruộng nào. Hãy nhập thông tin ở phía trên.';
  return;
 }
 list.innerHTML = farms.map(f =>
  '<div style="padding:12px 0;border-bottom:1px solid #eee">' +
  '<b>🌾 ' + esc(f.name || 'Chưa đặt tên') + '</b><br>' +
  '<small>Giống: ' + esc(f.variety || 'Chưa nhập') +
  ' · Diện tích: ' + esc(f.area || '0') + ' ha</small><br>' +
  '<small>Ngày sạ: ' + esc(f.sowDate || 'Chưa nhập') + '</small><br>' +
  '<button style="width:auto;padding:8px 12px" onclick="editFarm(' + Number(f.id) + ')">Sửa</button> ' +
  '<button style="width:auto;padding:8px 12px;background:#b83232" onclick="deleteFarm(' + Number(f.id) + ')">Xóa</button>' +
  '</div>'
 ).join('');
}

function editFarm(id){
 const farm = getFarms().find(f => f.id === id);
 if (!farm) {
  alert('Không tìm thấy ruộng.');
  return;
 }
 editingFarmId = id;
 fieldName.value = farm.name || '';
 variety.value = farm.variety || '';
 area.value = farm.area || '';
 sowDate.value = farm.sowDate || '';
 const saveButton = document.querySelector('#farm button');
 if (saveButton) saveButton.textContent = 'Lưu thay đổi';
 document.getElementById('farmResult').style.display = 'block';
 document.getElementById('farmResult').textContent = 'Đang sửa: ' + farm.name;
 document.getElementById('farm').scrollIntoView({behavior:'smooth'});
}

function deleteFarm(id){
 const farms = getFarms();
 const farm = farms.find(f => f.id === id);
 if (!farm) return;
 if (!confirm('Bạn có chắc muốn xóa ruộng "' + farm.name + '" không?')) return;
 const updated = farms.filter(f => f.id !== id);
 try {
  localStorage.setItem('nx_farms', JSON.stringify(updated));
 } catch (error) {
  alert('Không thể cập nhật danh sách ruộng.');
  return;
 }
 if (editingFarmId === id) {
  editingFarmId = null;
  fieldName.value = '';
  variety.value = '';
  area.value = '';
  sowDate.value = '';
  const saveButton = document.querySelector('#farm button');
  if (saveButton) saveButton.textContent = 'Lưu thông tin ruộng';
 }
 renderFarms();
}

function loadFarm(){
 const farms = getFarms();
 if (farms.length) {
  const d = farms[0];
  fieldName.value = d.name || '';
  variety.value = d.variety || '';
  area.value = d.area || '';
  sowDate.value = d.sowDate || '';
 }
 renderFarms();
}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function getTasks(){
 try {
  const tasks = JSON.parse(localStorage.getItem('nx_tasks') || '[]');
  if (!Array.isArray(tasks)) return [];
  let changed = false;
  tasks.forEach((task, i) => {
   if (!task.id) {
    task.id = 'care_' + Date.now() + '_' + i;
    changed = true;
   }
  });
  if (changed) localStorage.setItem('nx_tasks', JSON.stringify(tasks));
  return tasks;
 } catch (error) {
  return [];
 }
}

function syncCareReminder(task){
 if (!task || !task.id || !task.date || task.done) return;
 if (window.AndroidCare && typeof window.AndroidCare.scheduleReminder === 'function'){
  window.AndroidCare.scheduleReminder(String(task.id), String(task.name || 'Chăm sóc ruộng lúa'), String(task.date));
 }
}

function cancelCareReminder(task){
 if (!task || !task.id) return;
 if (window.AndroidCare && typeof window.AndroidCare.cancelReminder === 'function'){
  window.AndroidCare.cancelReminder(String(task.id));
 }
}

function syncAllCareReminders(){
 getTasks().forEach(task => {
  if (task.done) cancelCareReminder(task);
  else syncCareReminder(task);
 });
}

function renderTaskFarmOptions(){
 const select = document.getElementById('taskFarm');
 if (!select) return;
 const previous = select.value;
 const farms = getFarms();
 select.innerHTML = '<option value="">Tất cả ruộng / chưa chọn</option>' +
  farms.map(f => '<option value="' + Number(f.id) + '">' +
   esc(f.name || 'Ruộng chưa đặt tên') + '</option>').join('');
 if ([...select.options].some(o => o.value === previous)) {
  select.value = previous;
 }
}

function addTask(){
 const name = document.getElementById('taskName').value.trim();
 const date = document.getElementById('taskDate').value;
 const type = document.getElementById('taskType').value;
 const farmValue = document.getElementById('taskFarm').value;
 if (!name || !date) {
  alert('Bạn hãy nhập nội dung công việc và ngày thực hiện.');
  return;
 }
 const tasks = getTasks();
 const task = {id:'care_' + Date.now() + '_' + Math.random().toString(36).slice(2), name:name, date:date, done:false, type:type};
 if (farmValue !== '') {
  task.farmId = Number(farmValue);
  const farm = getFarms().find(f => f.id === task.farmId);
  task.farmName = farm ? farm.name : '';
 }
 tasks.push(task);
 try {
  localStorage.setItem('nx_tasks', JSON.stringify(tasks));
 } catch (error) {
  alert('Không lưu được lịch. Bộ nhớ có thể đã đầy.');
  return;
 }
 syncCareReminder(task);
 document.getElementById('taskName').value = '';
 renderTasks();
}

function renderTasks(){
 const tasks = getTasks();
 const list = document.getElementById('taskList');
 if (!list) return;

 if (!tasks.length) {
  list.textContent = 'Chưa có công việc nào.';
  return;
 }

 const today = new Date();
 const todayText = [
  today.getFullYear(),
  String(today.getMonth()+1).padStart(2,'0'),
  String(today.getDate()).padStart(2,'0')
 ].join('-');

 const ordered = tasks.map((task, index) => ({task, index}));
 ordered.sort((a,b) => {
  if (a.task.done !== b.task.done) return a.task.done ? 1 : -1;
  return String(a.task.date || '9999-99-99')
   .localeCompare(String(b.task.date || '9999-99-99'));
 });

 list.innerHTML = ordered.map(({task:t,index:i}) => {
  let status = '📅 Sắp tới';
  let color = '#16803c';

  if (t.done) {
   status = '✅ Đã hoàn thành';
   color = '#16803c';
  } else if (!t.date) {
   status = '⚪ Chưa có ngày';
   color = '#666';
  } else if (t.date < todayText) {
   status = '🔴 Quá hạn';
   color = '#c62828';
  } else if (t.date === todayText) {
   status = '🟠 Hôm nay';
   color = '#c77700';
  }

  return '<div style="padding:12px 0;border-bottom:1px solid #eee">' +
   '<div style="color:' + color + ';font-weight:bold;margin-bottom:5px">' +
   status + '</div>' +
   '<label style="margin:0"><input style="width:auto" type="checkbox" ' +
   (t.done ? 'checked' : '') +
   ' onchange="toggleTask(' + i + ',this.checked)"> ' +
   (t.done ? '<s>' : '') + esc(t.name || 'Công việc chưa đặt tên') +
   (t.done ? '</s>' : '') + '</label><br>' +
   '<small>📅 ' + esc(t.date || 'Chưa có ngày') +
   ' · ' + esc(t.type || 'Công việc cũ') +
   ' · 🌾 ' + esc(t.farmName || 'Chưa gắn ruộng') +
   '</small><br>' +
   '<button style="width:auto;padding:6px 10px;margin:5px 0;background:#b83232" ' +
   'onclick="deleteTask(' + i + ')">Xóa</button></div>';
 }).join('');
}
function toggleTask(i, value){
 const tasks = getTasks();
 if (!tasks[i]) return;
 tasks[i].done = value;
 localStorage.setItem('nx_tasks', JSON.stringify(tasks));
 if (value) cancelCareReminder(tasks[i]);
 else syncCareReminder(tasks[i]);
 renderTasks();
}

function deleteTask(i){
 if (!confirm('Bạn có chắc muốn xóa công việc này không?')) return;
 const tasks = getTasks();
 if (!tasks[i]) return;
 cancelCareReminder(tasks[i]);
 tasks.splice(i, 1);
 localStorage.setItem('nx_tasks', JSON.stringify(tasks));
 renderTasks();
}
function calculate(){
 const w=Number(weight.value),p=Number(price.value),c=Number(cost.value||0);
 if(weight.value===''||price.value===''||w<0||p<0||c<0){alert('Vui lòng nhập số liệu hợp lệ.');return;}
 const revenue=w*p,profit=revenue-c;
 calcResult.style.display='block';
 calcResult.innerHTML='Khối lượng: <b>'+w.toLocaleString('vi-VN')+' kg</b><br>Tiền bán: <b>'+revenue.toLocaleString('vi-VN')+' đ</b><br>Chi phí: <b>'+c.toLocaleString('vi-VN')+' đ</b><hr>Lãi/lỗ tạm tính: <b>'+profit.toLocaleString('vi-VN')+' đ</b>';
}

const diseasePhoto = document.getElementById('diseasePhoto');
const photoPreview = document.getElementById('photoPreview');
const diseaseStatus = document.getElementById('diseaseStatus');
const diseaseFarm = document.getElementById('diseaseFarm');
const diseaseHistoryFarm = document.getElementById('diseaseHistoryFarm');
const diseaseHistory = document.getElementById('diseaseHistory');

let selectedDiseaseImage = null;

function renderDiseaseFarmOptions() {
  const farms = getFarms();
  const currentFarm = diseaseFarm.value;
  const currentFilter = diseaseHistoryFarm.value;

  diseaseFarm.replaceChildren();
  const noFarm = document.createElement('option');
  noFarm.value = '';
  noFarm.textContent = 'Chưa gắn ruộng';
  diseaseFarm.appendChild(noFarm);

  diseaseHistoryFarm.replaceChildren();
  const allFarms = document.createElement('option');
  allFarms.value = '';
  allFarms.textContent = 'Tất cả ruộng';
  diseaseHistoryFarm.appendChild(allFarms);

  farms.forEach(farm => {
    const id = String(farm.id);
    const name = farm.name || 'Ruộng chưa đặt tên';

    const option = document.createElement('option');
    option.value = id;
    option.textContent = name;
    diseaseFarm.appendChild(option);

    const filterOption = document.createElement('option');
    filterOption.value = id;
    filterOption.textContent = name;
    diseaseHistoryFarm.appendChild(filterOption);
  });

  if ([...diseaseFarm.options].some(o => o.value === currentFarm)) {
    diseaseFarm.value = currentFarm;
  }
  if ([...diseaseHistoryFarm.options].some(o => o.value === currentFilter)) {
    diseaseHistoryFarm.value = currentFilter;
  }
}

diseasePhoto.addEventListener('change', function () {
  const file = this.files && this.files[0];
  if (!file) return;

  if (!file.type.startsWith('image/')) {
    alert('Bạn hãy chọn một file ảnh.');
    this.value = '';
    return;
  }

  if (file.size > 8 * 1024 * 1024) {
    alert('Ảnh quá lớn. Bạn hãy chọn ảnh nhỏ hơn 8 MB.');
    this.value = '';
    return;
  }

  const reader = new FileReader();
  reader.onload = function (event) {
    selectedDiseaseImage = {
      name: file.name,
      type: file.type,
      data: event.target.result,
      date: new Date().toISOString(),
      status: 'waiting'
    };

    photoPreview.replaceChildren();
    const img = document.createElement('img');
    img.src = selectedDiseaseImage.data;
    img.alt = 'Ảnh cây lúa cần kiểm tra';
    img.style.width = '100%';
    img.style.maxHeight = '300px';
    img.style.objectFit = 'contain';
    img.style.borderRadius = '12px';
    photoPreview.appendChild(img);

    diseaseStatus.style.display = 'block';
    diseaseStatus.textContent = 'Đã chọn ảnh. Nhấn nút lưu để lưu vào lịch sử.';
  };
  reader.readAsDataURL(file);
});


async function compressDiseaseImage(dataUrl) {
  const img = new Image();
  img.src = dataUrl;

  await new Promise((resolve, reject) => {
    img.onload = resolve;
    img.onerror = () => reject(new Error("Không đọc được ảnh."));
  });

  const scale = Math.min(
    1,
    1280 / Math.max(img.naturalWidth, img.naturalHeight)
  );

  const canvas = document.createElement("canvas");
  canvas.width = Math.max(1, Math.round(img.naturalWidth * scale));
  canvas.height = Math.max(1, Math.round(img.naturalHeight * scale));

  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Không xử lý được ảnh trên thiết bị.");

  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

  let quality = 0.82;
  let result = canvas.toDataURL("image/jpeg", quality);

  while (result.length > 4700000 && quality > 0.42) {
    quality -= 0.1;
    result = canvas.toDataURL("image/jpeg", quality);
  }

  if (result.length > 4700000) {
    throw new Error("Ảnh vẫn quá lớn. Hãy chọn ảnh khác.");
  }

  return result;
}

async function saveDiseasePhoto() {
  if (!selectedDiseaseImage) {
    alert("Bạn hãy chụp hoặc chọn ảnh trước nhé.");
    return;
  }

  const button = document.querySelector(
    '#disease button[onclick="saveDiseasePhoto()"]'
  );
  if (button) {
    button.disabled = true;
    button.textContent = "⏳ Đang phân tích ảnh...";
  }

  diseaseStatus.style.display = "block";
  diseaseStatus.textContent = "Đang tối ưu ảnh và gửi đến AI. Vui lòng chờ...";

  try {
    const original = selectedDiseaseImage;
    const imageData = await compressDiseaseImage(original.data);

    const farmId = diseaseFarm.value;
    const farm = getFarms().find(f => String(f.id) === farmId);

    const photo = {
      name: original.name,
      type: "image/jpeg",
      data: imageData,
      date: new Date().toISOString(),
      farmId: farm ? farm.id : "",
      farmName: farm
        ? (farm.name || "Ruộng chưa đặt tên")
        : "Chưa gắn ruộng",
      status: "error",
      result: "",
      error: ""
    };

    try {
      const response = await fetch(
        "https://nongnghiep-xanh-ai.nguyenduytuong093.workers.dev/diagnose",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image: imageData })
        }
      );

      const data = await response.json().catch(() => ({}));

      if (!response.ok || !data.ok || !data.result) {
        throw new Error(
          data.error || ("Máy chủ trả về HTTP " + response.status)
        );
      }

      photo.status = "done";
      photo.result = typeof data.result === "string"
        ? data.result
        : JSON.stringify(data.result, null, 2);
    } catch (error) {
      photo.error = error.message || "Không gọi được AI.";
    }

    const saved = JSON.parse(
      localStorage.getItem("nx_disease_photos") || "[]"
    );
    if (!Array.isArray(saved)) {
      throw new Error("Dữ liệu lịch sử ảnh không hợp lệ.");
    }

    saved.push(photo);
    localStorage.setItem("nx_disease_photos", JSON.stringify(saved));

    selectedDiseaseImage = null;
    diseasePhoto.value = "";
    photoPreview.replaceChildren();

    diseaseStatus.textContent = photo.status === "done"
      ? "✅ AI đã phân tích ảnh. Xem kết quả trong lịch sử bên dưới."
      : "Ảnh đã lưu, nhưng AI chưa phân tích được: " + photo.error;

    loadDiseasePhotos();
  } catch (error) {
    diseaseStatus.textContent =
      "Không hoàn tất được: " + (error.message || "Lỗi không xác định.");
  } finally {
    if (button) {
      button.disabled = false;
      button.textContent = "💾 Lưu ảnh và phân tích AI";
    }
  }
}

function loadDiseasePhotos() {
  renderDiseaseFarmOptions();

  try {
    const saved = JSON.parse(
      localStorage.getItem("nx_disease_photos") || "[]"
    );
    const photos = Array.isArray(saved) ? saved : [];

    diseaseStatus.style.display = "block";
    diseaseStatus.textContent = photos.length
      ? "Đã lưu " + photos.length + " ảnh trên thiết bị."
      : "Chưa có ảnh nào được lưu.";

    diseaseHistory.replaceChildren();

    const filterId = diseaseHistoryFarm.value;
    const filtered = photos.filter(photo =>
      !filterId || String(photo.farmId || "") === filterId
    );

    if (!filtered.length) {
      diseaseHistory.textContent = "Chưa có ảnh trong mục này.";
      return;
    }

    filtered.slice().reverse().forEach(photo => {
      const card = document.createElement("div");
      card.style.cssText = "padding:12px 0;border-bottom:1px solid #ddd";

      if (photo.data) {
        const img = document.createElement("img");
        img.src = photo.data;
        img.alt = "Ảnh đã lưu: " + (photo.name || "ảnh cây lúa");
        img.style.cssText =
          "width:100%;max-height:220px;object-fit:contain;border-radius:10px";
        card.appendChild(img);
      }

      const info = document.createElement("p");
      const date = photo.date ? new Date(photo.date) : null;
      const dateText = date && !Number.isNaN(date.getTime())
        ? date.toLocaleString("vi-VN")
        : "Không rõ ngày lưu";

      info.textContent =
        (photo.name || "Ảnh cây lúa") + " · " + dateText +
        " · Ruộng: " + (photo.farmName || "Chưa gắn ruộng");
      card.appendChild(info);

      const status = document.createElement("b");
      status.textContent = photo.status === "done"
        ? "✅ Đã phân tích bằng AI"
        : photo.error
          ? "⚠️ Chưa phân tích được: " + photo.error
          : "⏳ Chưa có kết quả phân tích";
      card.appendChild(status);

      if (photo.result) {
        const heading = document.createElement("h4");
        heading.textContent = "🤖 Kết quả AI";
        card.appendChild(heading);

        const result = document.createElement("p");
        result.style.whiteSpace = "pre-wrap";
        result.textContent = photo.result;
        card.appendChild(result);

        const note = document.createElement("small");
        note.textContent =
          "Kết quả chỉ mang tính tham khảo. Hãy kiểm tra thực tế và hỏi cán bộ bảo vệ thực vật trước khi quyết định dùng thuốc.";
        card.appendChild(note);
      }

      diseaseHistory.appendChild(card);
    });
  } catch (error) {
    diseaseHistory.textContent =
      "Không đọc được lịch sử ảnh. Bộ nhớ thiết bị có thể đã đầy.";
    console.error("Lỗi lịch sử ảnh:", error);
  }
}


loadDiseasePhotos();


function getTransactions() {
  try {
    return JSON.parse(localStorage.getItem('nx_transactions') || '[]');
  } catch (error) {
    return [];
  }
}

function addTransaction() {
  const type = document.getElementById('txType').value;
  const category = document.getElementById('txCategory').value;
  const date = document.getElementById('txDate').value;
  const note = document.getElementById('txNote').value.trim();
  const amount = Number(document.getElementById('txAmount').value);

  if (!date || !note || document.getElementById('txAmount').value === '' || !Number.isFinite(amount) || amount <= 0) {
    alert('Bạn hãy nhập ngày, nội dung và số tiền lớn hơn 0 nhé.');
    return;
  }

  const transactions = getTransactions();
  transactions.push({
    type: type,
    category: category,
    date: date,
    note: note,
    amount: amount
  });

  try {
    localStorage.setItem('nx_transactions', JSON.stringify(transactions));
  } catch (error) {
    alert('Không lưu được giao dịch. Bộ nhớ có thể đã đầy.');
    return;
  }

  document.getElementById('txNote').value = '';
  document.getElementById('txAmount').value = '';
  renderTransactions();
  alert('Đã lưu giao dịch!');
}

function deleteTransaction(index) {
  if (!confirm('Bạn có chắc muốn xóa giao dịch này không?')) return;

  const transactions = getTransactions();
  transactions.splice(index, 1);
  localStorage.setItem('nx_transactions', JSON.stringify(transactions));
  renderTransactions();
}

function renderTransactions() {
  const transactions = getTransactions();
  let income = 0;
  let expense = 0;

  transactions.forEach(function (t) {
    if (t.type === 'income') {
      income += Number(t.amount) || 0;
    } else {
      expense += Number(t.amount) || 0;
    }
  });

  document.getElementById('txIncome').textContent =
    income.toLocaleString('vi-VN') + ' đ';
  document.getElementById('txExpense').textContent =
    expense.toLocaleString('vi-VN') + ' đ';

  const profit = income - expense;
  const profitElement = document.getElementById('txProfit');
  profitElement.textContent = profit.toLocaleString('vi-VN') + ' đ';
  profitElement.style.color = profit >= 0 ? 'green' : 'red';

  const list = document.getElementById('txList');

  if (transactions.length === 0) {
    list.textContent = 'Chưa có giao dịch nào.';
    return;
  }

  list.innerHTML = transactions.map(function (t, i) {
    const isIncome = t.type === 'income';
    const sign = isIncome ? '+' : '-';
    const color = isIncome ? 'green' : 'red';

    return '<div style="padding:12px 0;border-bottom:1px solid #eee">' +
      '<b>' + esc(t.note) + '</b><br>' +
      '<small>' + esc(t.date) + ' · ' + esc(t.category) + '</small><br>' +
      '<b style="color:' + color + '">' + sign +
      (Number(t.amount) || 0).toLocaleString('vi-VN') + ' đ</b><br>' +
      '<button style="width:auto;padding:6px 10px;margin-top:6px" onclick="deleteTransaction(' +
      i + ')">Xóa</button>' +
      '</div>';
  }).join('');
}

document.getElementById('txDate').value =
  new Date().toLocaleDateString('sv-SE');

renderTransactions();


loadFarm();renderTaskFarmOptions();renderTasks();syncAllCareReminders();

async function loadWeather(){
  const latInput = document.getElementById('weatherLat');
  const lonInput = document.getElementById('weatherLon');
  const status = document.getElementById('weatherStatus');
  const currentBox = document.getElementById('weatherCurrent');
  const forecastBox = document.getElementById('weatherForecast');

  if(!latInput || !lonInput || !status || !currentBox || !forecastBox){
    console.error('Không tìm thấy giao diện thời tiết.');
    return;
  }

  const lat = Number(latInput.value);
  const lon = Number(lonInput.value);

  if(latInput.value.trim()==='' || lonInput.value.trim()==='' ||
     !Number.isFinite(lat) || !Number.isFinite(lon) ||
     lat < -90 || lat > 90 || lon < -180 || lon > 180){
    status.textContent = 'Vui lòng nhập vĩ độ từ -90 đến 90 và kinh độ từ -180 đến 180.';
    return;
  }

  status.textContent = 'Đang tải dữ liệu thời tiết...';
  currentBox.style.display = 'none';
  forecastBox.style.display = 'none';

  const descriptions = {
    0:'Trời quang',1:'Ít mây',2:'Có mây',3:'Nhiều mây',
    45:'Có sương mù',48:'Sương mù dày',
    51:'Mưa phùn nhẹ',53:'Mưa phùn vừa',55:'Mưa phùn dày',
    56:'Mưa phùn lạnh nhẹ',57:'Mưa phùn lạnh dày',
    61:'Mưa nhẹ',63:'Mưa vừa',65:'Mưa to',
    66:'Mưa lạnh nhẹ',67:'Mưa lạnh to',
    71:'Tuyết nhẹ',73:'Tuyết vừa',75:'Tuyết dày',77:'Mưa tuyết',
    80:'Mưa rào nhẹ',81:'Mưa rào vừa',82:'Mưa rào mạnh',
    85:'Mưa tuyết nhẹ',86:'Mưa tuyết mạnh',
    95:'Có dông',96:'Dông có mưa đá nhẹ',99:'Dông có mưa đá mạnh'
  };

  try{
    const url = 'https://api.open-meteo.com/v1/forecast?' +
      new URLSearchParams({
        latitude:String(lat),
        longitude:String(lon),
        current:'temperature_2m,relative_humidity_2m,precipitation,weather_code',
        daily:'precipitation_probability_max,temperature_2m_max,temperature_2m_min',
        timezone:'Asia/Ho_Chi_Minh',
        forecast_days:'7'
      }).toString();

    const response = await fetch(url);
    if(!response.ok) throw new Error('Máy chủ thời tiết trả về mã ' + response.status);
    const data = await response.json();

    if(!data.current || !data.daily) throw new Error('Dữ liệu thời tiết không đầy đủ.');

    const c = data.current;
    const d = data.daily;
    const code = Number(c.weather_code);
    const description = descriptions[code] || 'Chưa xác định';
    const fmt = n => Number.isFinite(Number(n)) ? Number(n).toLocaleString('vi-VN',{maximumFractionDigits:1}) : '--';
    const escWeather = v => String(v).replace(/[&<>"']/g, ch => ({
      '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
    }[ch]));

    currentBox.innerHTML =
      '<h3>🌤️ Thời tiết hiện tại</h3>' +
      '<p><b>' + escWeather(description) + '</b></p>' +
      '<p>🌡️ Nhiệt độ: <b>' + fmt(c.temperature_2m) + ' °C</b></p>' +
      '<p>💧 Độ ẩm: <b>' + fmt(c.relative_humidity_2m) + '%</b></p>' +
      '<p>🌧️ Lượng mưa: <b>' + fmt(c.precipitation) + ' mm</b></p>' +
      '<small>Thời điểm dữ liệu: ' + escWeather(c.time || '') + '</small>';
    currentBox.style.display = 'block';

    let rows = '';
    for(let i=0;i<(d.time || []).length;i++){
      rows += '<tr><td>' + escWeather(d.time[i]) + '</td>' +
        '<td>' + fmt(d.temperature_2m_min[i]) + ' °C</td>' +
        '<td>' + fmt(d.temperature_2m_max[i]) + ' °C</td>' +
        '<td>' + fmt(d.precipitation_probability_max[i]) + '%</td></tr>';
    }

    forecastBox.innerHTML =
      '<h3>📅 Dự báo 7 ngày</h3>' +
      '<div style="overflow-x:auto"><table style="width:100%;border-collapse:collapse">' +
      '<thead><tr><th>Ngày</th><th>Thấp nhất</th><th>Cao nhất</th><th>Khả năng mưa</th></tr></thead>' +
      '<tbody>' + rows + '</tbody></table></div>' +
      '<small>Nguồn dữ liệu: Open-Meteo. Dự báo chỉ mang tính tham khảo.</small>';
    forecastBox.style.display = 'block';
    status.textContent = 'Đã cập nhật thời tiết thành công!';
  }catch(error){
    console.error('Lỗi thời tiết:', error);
    status.textContent = 'Không tải được thời tiết. Hãy kiểm tra Internet và thử lại. Chi tiết: ' + error.message;
  }
}



// ===== Tài khoản Nông Nghiệp Xanh =====
(() => {
  const API = "https://nongnghiep-xanh-ai.nguyenduytuong093.workers.dev";
  const overlay = document.getElementById('nxAuthOverlay');
  const form = document.getElementById('nxAuthForm');
  const username = document.getElementById('nxUsername');
  const password = document.getElementById('nxPassword');
  const submit = document.getElementById('nxAuthSubmit');
  const switchBtn = document.getElementById('nxAuthSwitch');
  const message = document.getElementById('nxAuthMessage');
  const bar = document.getElementById('nxAccountBar');
  const accountName = document.getElementById('nxAccountName');
  const logoutBtn = document.getElementById('nxLogout');

  let mode = 'login';
  let busy = false;
  let token = null;

  function say(text, good = false) {
    message.textContent = text;
    message.style.color = good ? '#176b3a' : '#a52b2b';
  }

  function showSignedOut(text = '') {
    token = null;
    try { sessionStorage.removeItem('nx_auth_token'); } catch (_) {}
    overlay.hidden = false;
    bar.hidden = true;
    accountName.textContent = '';
    password.value = '';
    if (text) say(text);
  }

  function showSignedIn(user) {
    overlay.hidden = true;
    bar.hidden = false;
    accountName.textContent = user.username;
    password.value = '';
  }

  async function api(path, options = {}) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) headers.Authorization = 'Bearer ' + token;
    const response = await fetch(API + path, {
      method: options.method || 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined
    });
    let data = {};
    try { data = await response.json(); } catch (_) {}
    if (!response.ok) throw new Error(data.error || 'Yêu cầu thất bại (' + response.status + ').');
    return data;
  }

  switchBtn.addEventListener('click', () => {
    mode = mode === 'login' ? 'register' : 'login';
    submit.textContent = mode === 'login' ? 'Đăng nhập' : 'Tạo tài khoản';
    password.autocomplete = mode === 'login' ? 'current-password' : 'new-password';
    switchBtn.textContent = mode === 'login'
      ? 'Chưa có tài khoản? Đăng ký'
      : 'Đã có tài khoản? Đăng nhập';
    say(mode === 'register'
      ? 'Tên tài khoản từ 3–24 ký tự, chỉ gồm chữ, số và dấu gạch dưới.'
      : '');
  });

  form.addEventListener('submit', async event => {
    event.preventDefault();
    if (busy) return;

    const name = username.value.trim();
    const pass = password.value;
    if (!/^[A-Za-z0-9_]{3,24}$/.test(name)) {
      say('Tên tài khoản phải có 3–24 ký tự: chữ, số hoặc dấu gạch dưới.');
      return;
    }
    if (pass.length < 8 || pass.length > 128) {
      say('Mật khẩu phải có từ 8 đến 128 ký tự.');
      return;
    }

    busy = true;
    submit.disabled = true;
    switchBtn.disabled = true;
    say(mode === 'login' ? 'Đang đăng nhập...' : 'Đang tạo tài khoản...', true);

    try {
      if (mode === 'register') {
        const result = await api('/auth/register', {
          method: 'POST',
          body: { username: name, password: pass }
        });
        mode = 'login';
        submit.textContent = 'Đăng nhập';
        password.autocomplete = 'current-password';
        switchBtn.textContent = 'Chưa có tài khoản? Đăng ký';
        password.value = '';
        say(result.message || 'Đăng ký thành công. Hãy đăng nhập.', true);
      } else {
        const result = await api('/auth/login', {
          method: 'POST',
          body: { username: name, password: pass }
        });
        if (!result.token || !result.user || !result.user.username) {
          throw new Error('Máy chủ trả về thông tin đăng nhập không hợp lệ.');
        }
        token = result.token;
        // Token chỉ được giữ trong sessionStorage, không lưu mật khẩu.
        try { sessionStorage.setItem('nx_auth_token', token); }
        catch (_) { throw new Error('Không thể lưu phiên trên thiết bị. Hãy thử lại.'); }
        showSignedIn(result.user);
      }
    } catch (error) {
      say(error.message || 'Không thể kết nối máy chủ.');
    } finally {
      busy = false;
      submit.disabled = false;
      switchBtn.disabled = false;
    }
  });

  logoutBtn.addEventListener('click', async () => {
    if (busy) return;
    busy = true;
    logoutBtn.disabled = true;
    try {
      if (token) {
        await api('/auth/logout', { method: 'POST' });
      }
      showSignedOut('Bạn đã đăng xuất.');
    } catch (error) {
      // Nếu máy chủ không xác nhận, giữ phiên hiện tại để tránh báo sai.
      say('Chưa xác nhận được đăng xuất: ' + error.message);
    } finally {
      busy = false;
      logoutBtn.disabled = false;
    }
  });

  async function init() {
    try {
      token = sessionStorage.getItem('nx_auth_token');
    } catch (_) {
      token = null;
    }
    if (!token) {
      showSignedOut();
      return;
    }
    try {
      const result = await api('/auth/me');
      if (!result.user) throw new Error('Phiên không hợp lệ.');
      showSignedIn(result.user);
    } catch (_) {
      showSignedOut('Phiên đăng nhập hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.');
    }
  }

  init();
})();

