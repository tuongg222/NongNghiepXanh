from pathlib import Path

s = Path("lib/screens/login_screen.dart").read_text()

stack = []
pairs = {')': '(', ']': '[', '}': '{'}
line = 1
i = 0
state = "code"

while i < len(s):
    c = s[i]
    n = s[i+1] if i+1 < len(s) else ""

    if c == "\n":
        line += 1

    if state == "code":
        if c == "/" and n == "/":
            state = "line"
            i += 1
        elif c == "/" and n == "*":
            state = "block"
            i += 1
        elif c in ("'", '"'):
            state = c
        elif c in "([{":
            stack.append((c, line))
        elif c in ")]}":
            if not stack or stack[-1][0] != pairs[c]:
                print("Ngoặc đóng sai tại dòng", line, c)
            else:
                stack.pop()

    elif state == "line":
        if c == "\n":
            state = "code"

    elif state == "block":
        if c == "*" and n == "/":
            state = "code"
            i += 1

    else:
        if c == "\\":
            i += 1
        elif c == state:
            state = "code"

    i += 1

print("Ngoặc chưa đóng:", stack)
print("Kiểm tra hoàn tất.")
