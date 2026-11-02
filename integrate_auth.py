from pathlib import Path
import re
import sys

p = Path("app/src/main/assets/index.html")
s = p.read_text(encoding="utf-8")
backup = p.with_name("index.html.before-auth.bak")

API = "https://nongnghiep-xanh-ai.nguyenduytuong093.workers.dev"

if 'id="nxAuthOverlay"' in s:
    print("Giao diện tài khoản đã được chèn trước đó. Không sửa thêm.")
    sys.exit(0)

if not backup.exists():
    backup.write_text(s, encoding="utf-8")

css = r"""
#nxAuthOverlay{position:fixed;inset:0;z-index:99999;background:#f2f7f0;
display:flex;align-items:center;justify-content:center;padding:20px;overflow:auto}
#nxAuthOverlay[hidden]{display:none}
.nx-auth-card{width:100%;max-width:420px;background:white;border-radius:20px;
padding:22px;box-shadow:0 8px 30px #173d1720}
.nx-auth-logo{text-align:center;font-size:42px}
.nx-auth-card h2{text-align:center;color:#176b3a;margin:8px 0}
.nx-auth-card .nx-muted{text-align:center;color:#64756a;font-size:14px}
.nx-auth-card input{margin-bottom:8px}
.nx-auth-switch{background:#e4f3e5;color:#176b3a}
#nxAuthMessage{font-size:14px;line-height:1.5;margin-top:12px;overflow-wrap:anywhere}
#nxAccountBar{display:flex;align-items:center;justify-content:space-between;gap:8px;
padding:10px 16px;background:#e4f3e5;color:#176b3a;font-size:14px}
#nxAccountBar button{width:auto;margin:0;padding:8px 12px;font-size:14px}
"""

html = r"""
<div id="nxAuthOverlay">
  <div class="nx-auth-card">
    <div class="nx-auth-logo">🌱</div>
    <h2>Nông Nghiệp Xanh</h2>
    <p class="nx-muted">Đăng nhập để sử dụng ứng dụng</p>
    <form id="nxAuthForm">
      <label for="nxUsername">Tên tài khoản</label>
      <input id="nxUsername" name="username" autocomplete="username"
             minlength="3" maxlength="24" required
             pattern="[A-Za-z0-9_]{3,24}" placeholder="Tên tài khoản">
      <label for="nxPassword">Mật khẩu</label>
      <input id="nxPassword" name="password" type="password"
             autocomplete="current-password" required
             minlength="8" maxlength="128" placeholder="Mật khẩu">
      <button id="nxAuthSubmit" type="submit">Đăng nhập</button>
    </form>
    <button id="nxAuthSwitch" class="nx-auth-switch" type="button">
      Chưa có tài khoản? Đăng ký
    </button>
    <div id="nxAuthMessage" role="status" aria-live="polite"></div>
    <small>Thông tin tài khoản được xác thực qua máy chủ.</small>
  </div>
</div>
<div id="nxAccountBar" hidden>
  <span>👤 <b id="nxAccountName"></b></span>
  <button id="nxLogout" type="button">Đăng xuất</button>
</div>
"""

js = r"""
// ===== Tài khoản Nông Nghiệp Xanh =====
(() => {
  const API = "__NX_API__";
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
""".replace("__NX_API__", API)

if "</head>" not in s or "<body>" not in s or "</script>" not in s:
    print("Không tìm thấy cấu trúc HTML mong đợi; đã dừng để tránh làm hỏng file.")
    sys.exit(1)

s = s.replace("</style>", css + "\n</style>", 1)
s = s.replace("<body>", "<body>\n" + html, 1)

# Chèn script trước thẻ script cuối cùng, giữ nguyên các script hiện có.
idx = s.rfind("</script>")
s = s[:idx] + "\n" + js + "\n" + s[idx:]

p.write_text(s, encoding="utf-8")
print("Đã tích hợp giao diện tài khoản.")
print("Bản sao lưu:", backup)
print("Dữ liệu localStorage nông nghiệp được giữ nguyên.")
