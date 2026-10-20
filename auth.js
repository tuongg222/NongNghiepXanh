const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json; charset=utf-8"
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: CORS });
}

function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return Array.from(bytes, b => b.toString(16).padStart(2, "0")).join("");
}

async function sha256(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), b =>
    b.toString(16).padStart(2, "0")
  ).join("");
}

async function passwordHash(password, salt) {
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    "raw",
    encoder.encode(password),
    "PBKDF2",
    false,
    ["deriveBits"]
  );

  const bits = await crypto.subtle.deriveBits(
    {
      name: "PBKDF2",
      salt: encoder.encode(salt),
      iterations: 210000,
      hash: "SHA-256"
    },
    key,
    256
  );

  return Array.from(new Uint8Array(bits), b =>
    b.toString(16).padStart(2, "0")
  ).join("");
}

function safeEqual(a, b) {
  if (a.length !== b.length) return false;
  let diff = 0;
  for (let i = 0; i < a.length; i++) diff |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return diff === 0;
}

export async function handleAuth(request, env, url) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (!env.DB) return json({ error: "D1 chưa được cấu hình." }, 503);

  if (request.method !== "POST") {
    return json({ error: "Chỉ chấp nhận POST." }, 405);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: "JSON không hợp lệ." }, 400);
  }

  if (url.pathname === "/auth/register") {
    const username = typeof body.username === "string" ? body.username.trim() : "";
    const password = typeof body.password === "string" ? body.password : "";

    if (!/^[a-zA-Z0-9_]{3,24}$/.test(username)) {
      return json({ error: "Tên tài khoản phải dài 3–24 ký tự, chỉ gồm chữ, số và dấu gạch dưới." }, 400);
    }
    if (password.length < 10 || password.length > 128) {
      return json({ error: "Mật khẩu phải dài từ 10 đến 128 ký tự." }, 400);
    }

    let stage = "randomToken";
    try {
      const salt = randomToken();
      stage = "passwordHash";
      const hash = await passwordHash(password, salt);
      const stored = `${salt}:${hash}`;

      stage = "D1_INSERT";
      await env.DB.prepare(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)"
      ).bind(username, stored).run();

      return json({ ok: true, message: "Đăng ký thành công. Bạn có thể đăng nhập." }, 201);
    } catch (error) {
      if (String(error?.message || "").toLowerCase().includes("unique")) {
        return json({ error: "Tên tài khoản đã tồn tại." }, 409);
      }
      console.error("Register failed at", stage, error?.name || "UnknownError");
      return json({ error: "Lỗi đăng ký.", stage, code: error?.name || "UnknownError" }, 500);
    }
  }

  if (url.pathname === "/auth/login") {
    const username = typeof body.username === "string" ? body.username.trim() : "";
    const password = typeof body.password === "string" ? body.password : "";

    if (!username || !password) {
      return json({ error: "Vui lòng nhập tên tài khoản và mật khẩu." }, 400);
    }

    const user = await env.DB.prepare(
      "SELECT id, username, password_hash FROM users WHERE username = ?"
    ).bind(username).first();

    if (!user || typeof user.password_hash !== "string") {
      return json({ error: "Tên tài khoản hoặc mật khẩu không đúng." }, 401);
    }

    const [salt, savedHash] = user.password_hash.split(":");
    if (!salt || !savedHash) return json({ error: "Thông tin tài khoản không hợp lệ." }, 500);

    const candidate = await passwordHash(password, salt);
    if (!safeEqual(candidate, savedHash)) {
      return json({ error: "Tên tài khoản hoặc mật khẩu không đúng." }, 401);
    }

    const token = randomToken();
    const tokenHash = await sha256(token);
    const expiresAt = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60;

    await env.DB.prepare(
      "INSERT INTO sessions (user_id, token_hash, expires_at) VALUES (?, ?, ?)"
    ).bind(user.id, tokenHash, expiresAt).run();

    return json({
      ok: true,
      token,
      expiresAt,
      user: { id: user.id, username: user.username }
    });
  }

  if (url.pathname === "/auth/me" || url.pathname === "/auth/logout") {
    const auth = request.headers.get("Authorization") || "";
    const match = auth.match(/^Bearer ([a-f0-9]{64})$/i);
    if (!match) return json({ error: "Bạn chưa đăng nhập." }, 401);

    const tokenHash = await sha256(match[1]);
    const session = await env.DB.prepare(
      "SELECT s.user_id, s.expires_at, u.username FROM sessions s JOIN users u ON u.id = s.user_id WHERE s.token_hash = ?"
    ).bind(tokenHash).first();

    if (!session || session.expires_at <= Math.floor(Date.now() / 1000)) {
      if (session) {
        await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(tokenHash).run();
      }
      return json({ error: "Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại." }, 401);
    }

    if (url.pathname === "/auth/logout") {
      await env.DB.prepare("DELETE FROM sessions WHERE token_hash = ?").bind(tokenHash).run();
      return json({ ok: true, message: "Đã đăng xuất." });
    }

    return json({
      ok: true,
      user: { id: session.user_id, username: session.username },
      expiresAt: session.expires_at
    });
  }

  return json({ error: "Không tìm thấy API tài khoản." }, 404);
}
