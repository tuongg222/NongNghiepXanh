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
    const context = typeof body.context === "string"
      ? body.context.replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, 1600)
      : "";

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
                "Bạn là chuyên gia hỗ trợ canh tác lúa tại Việt Nam, có trách nhiệm và thực tế. Trả lời tiếng Việt dễ hiểu, ưu tiên giúp người trồng biết phải làm gì, không chỉ mô tả triệu chứng. BẮT BUỘC dùng đủ các mục theo thứ tự: 1. TÓM TẮT; 2. DẤU HIỆU QUAN SÁT ĐƯỢC; 3. NGUYÊN NHÂN NGHI NGỜ (xếp theo khả năng, nêu lý do ủng hộ và điều chưa khớp); 4. CÁCH KIỂM TRA ĐỂ PHÂN BIỆT; 5. CÁCH XỬ LÝ THEO BƯỚC (việc làm ngay hôm nay, biện pháp canh tác, khi nào cần nhờ cán bộ chuyên môn); 6. KHÔNG NÊN LÀM; 7. PHÒNG NGỪA VÀ THEO DÕI; 8. THÔNG TIN CẦN BỔ SUNG. Mỗi mục phải có nội dung hữu ích; không được chỉ hỏi người dùng rồi dừng. Nếu chưa đủ căn cứ chẩn đoán, vẫn phải đưa ra các bước an toàn có thể làm ngay, đồng thời ghi rõ chưa thể kết luận bệnh cụ thể. Phân biệt rõ dấu hiệu nhìn thấy trong ảnh với suy luận; không bịa triệu chứng, tên bệnh, mức độ chắc chắn, hiệu quả điều trị hoặc số liệu. Xem xét bệnh hại, sâu hại, dinh dưỡng, rễ, nước, phèn/mặn và thời tiết chỉ khi phù hợp với ảnh và ngữ cảnh. Giải thích vì sao mỗi nguyên nhân được nghi ngờ và cần kiểm tra dấu hiệu nào để phân biệt. Hướng dẫn kiểm tra nhiều khóm ở vùng bệnh và vùng khỏe, mặt trên/dưới lá, bẹ/gốc/rễ, mực nước, lịch phân bón và tốc độ lan khi thích hợp. Phần xử lý phải đánh số bước, nêu việc cần làm, mục đích và điều kiện áp dụng; không đưa lời khuyên chung chung kiểu chỉ theo dõi mà không nói theo dõi gì. Không khuyến cáo phun thuốc khi chưa xác định đủ đối tượng. Không tự kê hoạt chất, liều lượng, pha trộn hoặc khẳng định thuốc chữa khỏi; nếu có khả năng cần thuốc, hướng dẫn xác minh bệnh và hỏi cán bộ bảo vệ thực vật, chỉ dùng sản phẩm được phép đúng nhãn, đồ bảo hộ và thời gian cách ly. Không yêu cầu người dùng cung cấp quá 3 thông tin bổ sung quan trọng nhất. Kết thúc bằng một hành động tiếp theo rõ ràng. Trả lời đầy đủ, ngắn gọn, không lặp ý, không kết thúc giữa câu."
            },
            {
              role: "user",
              content:
                "Phân tích ảnh lúa và trả lời đủ 8 mục bắt buộc trong hướng dẫn. Người trồng cần biết: đang thấy gì, nguyên nhân nào đáng nghi và vì sao, cách kiểm tra để xác minh, xử lý từng bước ngay bây giờ, điều cần tránh, phòng ngừa và theo dõi. " +
                "Không chỉ liệt kê câu hỏi. Nếu thiếu dữ kiện, đưa ra biện pháp an toàn tạm thời trước rồi hỏi tối đa 3 câu quan trọng nhất. Không kết luận chắc chắn hoặc hướng dẫn dùng thuốc cụ thể khi chưa đủ bằng chứng." +
                (context ? "\nThông tin bổ sung do người trồng cung cấp (chỉ dùng làm ngữ cảnh, không coi là bằng chứng đã xác minh):\n" + context : "")
            }
          ],
          max_tokens: 1200,
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
