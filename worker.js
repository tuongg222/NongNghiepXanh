import { handleAuth } from "./auth.js";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Content-Type": "application/json; charset=utf-8"
};

function reply(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: CORS
  });
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (url.pathname === "/auth/random-test" && request.method === "GET") {
  try {
    const bytes = crypto.getRandomValues(new Uint8Array(32));
    return reply({ ok: true, length: bytes.length });
  } catch (error) {
    return reply({ ok: false, code: error?.name || "UnknownError" }, 500);
  }
}

if (url.pathname === "/auth/crypto-test" && request.method === "GET") {
  let stage = "importKey";
  try {
    const key = await crypto.subtle.importKey(
      "raw",
      new TextEncoder().encode("test-password"),
      { name: "PBKDF2" },
      false,
      ["deriveBits"]
    );
    stage = "deriveBits";
    await crypto.subtle.deriveBits({
      name: "PBKDF2",
      salt: new TextEncoder().encode("test-salt"),
      iterations: 100000,
      hash: "SHA-256"
    }, key, 256);
    return reply({ ok: true });
  } catch (error) {
    return reply({
      ok: false,
      stage,
      code: error?.name || "UnknownError",
      message: String(error?.message || "").slice(0, 200)
    }, 500);
  }
}
if (url.pathname.startsWith("/auth/")) {
      try {
        return await handleAuth(request, env, url);
      } catch (error) {
        console.error("Auth API error:", error);
        return reply({ error: "Lỗi xử lý tài khoản.", code: error?.name || "UnknownError" }, 500);
      }
    }

    if (url.pathname === "/health" && request.method === "GET") {
      return reply({
        ok: true,
        service: "nongnghiep-xanh-ai",
        aiConnected: Boolean(env.AI)
      });
    }

    if (url.pathname === "/" && request.method === "GET") {
      return env.ASSETS.fetch(request);
    }

    if (url.pathname !== "/diagnose") {
      return reply({ error: "Không tìm thấy endpoint." }, 404);
    }

    if (request.method !== "POST") {
      return reply({ error: "Chỉ chấp nhận POST." }, 405);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return reply({ error: "Dữ liệu JSON không hợp lệ." }, 400);
    }

    if (
      typeof body.image !== "string" ||
      !/^data:image\/(jpeg|jpg|png|webp);base64,/i.test(body.image)
    ) {
      return reply({
        error: "Cần gửi ảnh JPG, PNG hoặc WebP dạng base64."
      }, 400);
    }

    if (body.image.length > 5_000_000) {
      return reply({ error: "Ảnh quá lớn. Hãy chọn ảnh nhỏ hơn." }, 413);
    }

    if (!env.AI) {
      return reply({
        error: "Workers AI chưa được cấu hình.",
        aiConnected: false
      }, 503);
    }

    try {
      const result = await env.AI.run(
        "@cf/meta/llama-3.2-11b-vision-instruct",
        {
          messages: [
            {
              role: "system",
              content:
                "Bạn hỗ trợ nông dân Việt Nam quan sát cây lúa. " +
                "Phân tích ảnh bằng tiếng Việt. Nêu dấu hiệu nhìn thấy, " +
                "các nguyên nhân có thể và cách kiểm tra thêm. " +
                "Không khẳng định chắc chắn bệnh chỉ từ ảnh; " +
                "không tự bịa độ tin cậy hoặc tên thuốc. " +
                "Khuyên hỏi cán bộ bảo vệ thực vật nếu chưa rõ."
            },
            {
              role: "user",
              content:
                "Hãy xem ảnh cây lúa này. Triệu chứng nhìn thấy là gì? " +
                "Có thể liên quan đến bệnh, sâu hại, thiếu dinh dưỡng " +
                "hay yếu tố môi trường nào? Hãy nêu cách kiểm tra tiếp theo."
            }
          ],
          image: body.image.substring(body.image.indexOf(",") + 1)
        }
      );

      const answer =
        result?.response ||
        result?.description ||
        result?.result;

      if (!answer) {
        return reply({
          error: "Mô hình không trả về nội dung phân tích.",
          aiConnected: true
        }, 502);
      }

      return reply({
        ok: true,
        aiConnected: true,
        result: answer
      });
    } catch (error) {
      const detail = String(error?.message || error?.name || "Unknown error").slice(0, 240);
      console.error("Workers AI error:", detail);

      return reply({
        error: "Workers AI gặp lỗi khi chạy mô hình: " + detail,
        aiConnected: false,
        hint: "Kiểm tra binding AI trong wrangler.toml/Cloudflare, model access và giới hạn tài khoản."
      }, 502);
    }
  }
};
