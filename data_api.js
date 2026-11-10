const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, PUT, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json; charset=utf-8"
};

function reply(data, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: CORS });
}

async function sha256(value) {
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(value)
  );
  return Array.from(new Uint8Array(digest), b =>
    b.toString(16).padStart(2, "0")
  ).join("");
}

async function getUser(request, env) {
  const auth = request.headers.get("Authorization") || "";
  const match = auth.match(/^Bearer ([a-f0-9]{64})$/i);
  if (!match) return null;

  const tokenHash = await sha256(match[1]);
  const session = await env.DB.prepare(
    "SELECT user_id, expires_at FROM sessions WHERE token_hash = ?"
  ).bind(tokenHash).first();

  if (!session || session.expires_at <= Math.floor(Date.now() / 1000)) {
    return null;
  }

  return session.user_id;
}

const ALLOWED_KEYS = ["seasons", "journal", "finance", "prices"];

export async function handleData(request, env) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }

  if (!env.DB) return reply({ error: "D1 chưa cấu hình." }, 503);

  const userId = await getUser(request, env);
  if (!userId) return reply({ error: "Phiên đăng nhập không hợp lệ." }, 401);

  if (request.method === "GET") {
    const rows = await env.DB.prepare(
      "SELECT data_key, json_data, updated_at FROM user_data WHERE user_id = ?"
    ).bind(userId).all();

    const data = {};
    for (const row of rows.results || []) {
      try {
        data[row.data_key] = JSON.parse(row.json_data);
      } catch {
        data[row.data_key] = null;
      }
    }

    return reply({ ok: true, data });
  }

  if (request.method === "PUT") {
    let body;
    try {
      body = await request.json();
    } catch {
      return reply({ error: "JSON không hợp lệ." }, 400);
    }

    const key = body.key;
    if (!ALLOWED_KEYS.includes(key)) {
      return reply({ error: "Nhóm dữ liệu không hợp lệ." }, 400);
    }

    let jsonData;
    try {
      jsonData = JSON.stringify(body.data);
    } catch {
      return reply({ error: "Dữ liệu không thể chuyển thành JSON." }, 400);
    }

    if (typeof jsonData !== "string" || jsonData.length > 500000) {
      return reply({ error: "Dữ liệu vượt giới hạn 500 KB." }, 413);
    }

    await env.DB.prepare(
      `INSERT INTO user_data (user_id, data_key, json_data, updated_at)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(user_id, data_key)
       DO UPDATE SET json_data = excluded.json_data,
                     updated_at = excluded.updated_at`
    ).bind(userId, key, jsonData, Math.floor(Date.now() / 1000)).run();

    return reply({ ok: true, key });
  }

  return reply({ error: "Phương thức không được hỗ trợ." }, 405);
}
