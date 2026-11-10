from pathlib import Path

p = Path("worker.js")
s = p.read_text()

if 'url.pathname === "/chat"' in s:
    print("Endpoint /chat da ton tai, khong chen trung.")
    raise SystemExit(0)

marker = '    if (url.pathname !== "/diagnose") {'

if marker not in s:
    print("Khong tim thay vi tri chen endpoint.")
    raise SystemExit(1)

chat = r'''
    // NONG NGHIEP XANH - AI CHAT
    if (url.pathname === "/chat") {
      if (request.method !== "POST") {
        return reply({ error: "Chi chap nhan POST." }, 405);
      }

      if (!env.AI) {
        return reply({ error: "Workers AI chua duoc cau hinh." }, 503);
      }

      let body;
      try {
        body = await request.json();
      } catch {
        return reply({ error: "JSON khong hop le." }, 400);
      }

      const question = typeof body.message === "string"
        ? body.message.replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, 2000)
        : "";

      const context = typeof body.context === "string"
        ? body.context.replace(/[\u0000-\u001f]+/g, " ").trim().slice(0, 2000)
        : "";

      if (!question) {
        return reply({ error: "Hay nhap cau hoi." }, 400);
      }

      try {
        const result = await env.AI.run(
          "@cf/meta/llama-3.2-11b-vision-instruct",
          {
            messages: [
              {
                role: "system",
                content:
                  "Ban la Nong Nghiep Xanh AI, tro ly nong nghiep Viet Nam. " +
                  "Tra loi bang tieng Viet tu nhien, than thien, ro rang va de ap dung. " +
                  "Uu tien lua, cay trong, dat, nuoc, thoi tiet, dinh duong, sau benh, " +
                  "lich cham soc va kinh te mua vu. " +
                  "Giai thich vi sao, neu cac buoc thuc hien va dieu kien ap dung. " +
                  "Khong tu bia du lieu thoi tiet, gia nong san hay ket qua xet nghiem. " +
                  "Khong chan doan chac chan khi thieu bang chung. " +
                  "Khong tu dua lieu luong thuoc, pha tron hoa chat hay khuyen cao " +
                  "phun thuoc khi chua xac dinh doi tuong; huong dan tham khao " +
                  "can bo bao ve thuc vat va doc dung nhan san pham. " +
                  "Neu cau hoi ngoai nong nghiep, van tra loi lich su va huu ich."
              },
              {
                role: "user",
                content:
                  (context ? "Thong tin ruong/vuon:\n" + context + "\n\n" : "") +
                  "Cau hoi: " + question
              }
            ],
            max_tokens: 900
          }
        );

        const answer = result?.response || result?.description;
        if (!answer) {
          return reply({ error: "AI chua tao duoc cau tra loi." }, 502);
        }

        return reply({
          ok: true,
          aiConnected: true,
          answer: answer
        });
      } catch (error) {
        console.error("Chat AI error:", error);
        return reply({
          error: "AI chat loi: " + String(error?.message || error).slice(0, 250)
        }, 502);
      }
    }

'''

s = s.replace(marker, chat + marker, 1)
p.write_text(s)
print("Da them endpoint /chat thanh cong!")
