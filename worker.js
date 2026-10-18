const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
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

    if (url.pathname === "/health" && request.method === "GET") {
      return reply({
        ok: true,
        service: "nongnghiep-xanh-ai",
        aiConnected: Boolean(env.AI_API_KEY)
      });
    }

    if (url.pathname !== "/diagnose") {
      return reply({ error: "Khong tim thay endpoint." }, 404);
    }

    if (request.method !== "POST") {
      return reply({ error: "Chi chap nhan POST." }, 405);
    }

    let body;
    try {
      body = await request.json();
    } catch {
      return reply({ error: "Du lieu JSON khong hop le." }, 400);
    }

    if (typeof body.image !== "string" ||
        !/^data:image\/(jpeg|jpg|png|webp);base64,/i.test(body.image)) {
      return reply({
        error: "Can gui anh JPG, PNG hoac WebP dang base64."
      }, 400);
    }

    if (body.image.length > 5_000_000) {
      return reply({ error: "Anh qua lon. Hay chon anh nho hon." }, 413);
    }

    if (!env.AI_API_KEY) {
      return reply({
        error: "May chu chua duoc cau hinh AI.",
        aiConnected: false
      }, 503);
    }

    return reply({
      error: "AI chua duoc ket noi voi mo hinh nhan dien benh lua.",
      aiConnected: false
    }, 503);
  }
};
