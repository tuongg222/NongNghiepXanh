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
                "Bạn hỗ trợ nông dân Việt Nam đánh giá sơ bộ sức khỏe cây lúa qua ảnh. " +
                "Trả lời bằng tiếng Việt, rõ ràng và dễ làm theo. Phân biệt dấu hiệu nhìn thấy với giả thuyết; nêu tối đa 3 nguyên nhân có thể và cách phân biệt. " +
                "Không khẳng định chắc chắn bệnh chỉ từ ảnh, không bịa tên bệnh, độ tin cậy hoặc tên thuốc. " +
                "Nếu ảnh mờ hoặc thiếu căn cứ, hãy nói rõ giới hạn và đề nghị chụp thêm ảnh gần, trung cảnh và toàn cảnh. " +
                "Trình bày theo các mục: 1) Dấu hiệu quan sát; 2) Nguyên nhân có thể; 3) Cách kiểm tra ngoài ruộng; 4) Việc nên làm ngay; " +
                "5) Kế hoạch xử lý từng bước; 6) Theo dõi và đánh giá lại; 7) Phòng ngừa tái phát. " +
                "Ưu tiên quản lý dịch hại tổng hợp IPM, vệ sinh đồng ruộng, quản lý nước và dinh dưỡng phù hợp. " +
                "Không chỉ định hoạt chất, liều lượng hoặc pha trộn thuốc khi chưa xác định đúng đối tượng và kiểm tra nhãn được phép sử dụng tại địa phương. " +
                "Nếu cần thuốc, hướng dẫn người trồng hỏi cán bộ bảo vệ thực vật; tuân thủ nhãn, đồ bảo hộ và thời gian cách ly. " +
                "Nêu rõ khi nào cần liên hệ cán bộ bảo vệ thực vật địa phương."
            },
            {
              role: "user",
              content:
                "Hãy phân tích ảnh cây lúa này và hướng dẫn người trồng xử lý theo từng bước. " +
                "Mô tả dấu hiệu thực sự nhìn thấy; nêu các nguyên nhân có thể gồm bệnh, sâu hại, thiếu dinh dưỡng hoặc yếu tố môi trường. " +
                "Đề xuất cách kiểm tra để phân biệt nguyên nhân, việc có thể làm ngay, việc cần tránh, cách theo dõi và phòng ngừa. " +
                "Nếu chưa đủ bằng chứng, hãy hỏi thêm giai đoạn cây, vị trí và phạm vi triệu chứng, thời điểm xuất hiện, thời tiết và cách chăm sóc gần đây. " +
                "Không khẳng định bệnh hoặc đề xuất liều thuốc cụ thể nếu chưa đủ căn cứ."
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
      const detail = String(error?.message || error || "Unknown error");
      console.error("Workers AI error:", detail);
      if (detail.includes("5016") || /must submit the prompt ['\"]agree['\"]/i.test(detail)) {
        return reply({
          error: "Cloudflare yêu cầu chủ dự án chấp nhận giấy phép Meta Llama trước khi dùng mô hình. Mở Cloudflare Workers AI, chọn llama-3.2-11b-vision-instruct và hoàn tất bước chấp nhận giấy phép. Ứng dụng không tự đồng ý thay bạn.",
          code: "MODEL_LICENSE_REQUIRED",
          license: "https://github.com/meta-llama/llama-models/blob/main/models/llama3_2/LICENSE"
        }, 503);
      }
      return reply({
        error: "Workers AI gặp lỗi: " + detail.slice(0, 300),
        code: "WORKERS_AI_ERROR",
        aiConnected: false
      }, 502);
    }
  }
};
