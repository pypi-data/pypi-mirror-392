import sys
import os
import hashlib
import secrets
from typing import Tuple

PRIVATE_KEY_FILE = "private.key"
PUBLIC_KEY_FILE = "public.key"
DEFAULT_PARAMS_FILE = "params.txt"
DEFAULT_P = 33563
DEFAULT_Q = 173
DEFAULT_A = 10918


def read_params(params_path: str = DEFAULT_PARAMS_FILE) -> Tuple[int, int, int]:
    if not os.path.exists(params_path):
        return DEFAULT_P, DEFAULT_Q, DEFAULT_A
    p = q = a = None
    with open(params_path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.split("#", 1)[0].strip()
            if not ln:
                continue
            if "=" in ln:
                k, v = ln.split("=", 1)
                k = k.strip().lower()
                v = v.strip()
                if k == "p":
                    p = int(v)
                elif k == "q":
                    q = int(v)
                elif k == "a":
                    a = int(v)
    if p is None or q is None or a is None:
        raise ValueError("params.txt должен содержать p=, q= и a=")
    return p, q, a


def modinv(a: int, m: int) -> int:
    a %= m
    if a == 0:
        raise ZeroDivisionError("Inverse does not exist")
    lm, hm = 1, 0
    low, high = a, m
    while low > 1:
        r = high // low
        nm = hm - lm * r
        new = high - low * r
        hm, lm = lm, nm
        high, low = low, new
    return lm % m


def hash_to_int(data: bytes, q: int) -> int:
    h = hashlib.sha256(data).digest()
    hv = int.from_bytes(h, "big")
    return hv % q


def keygen(params_path: str = DEFAULT_PARAMS_FILE):
    p, q, a = read_params(params_path)
    x = secrets.randbelow(q - 1) + 1
    y = pow(a, x, p)
    with open(PRIVATE_KEY_FILE, "w", encoding="utf-8") as f:
        f.write(str(x) + "\n")
    with open(PUBLIC_KEY_FILE, "w", encoding="utf-8") as f:
        f.write(f"{p}\n{q}\n{a}\n{y}\n")
    print("Ключи сгенерированы.")
    print(f"private -> {PRIVATE_KEY_FILE}")
    print(f"public  -> {PUBLIC_KEY_FILE}")
    print(f"Параметры: p={p}, q={q}, a={a}")


def sign_file(in_path: str, out_path: str, params_path: str = DEFAULT_PARAMS_FILE):
    if not os.path.exists(PRIVATE_KEY_FILE):
        print("Ошибка: private.key не найден. Выполните keygen.")
        return
    with open(PRIVATE_KEY_FILE, "r", encoding="utf-8") as f:
        x = int(f.read().strip().splitlines()[0])
    p, q, a = read_params(params_path)
    msg = open(in_path, "rb").read()
    e = hash_to_int(msg, q)
    if e == 0:
        e = 1

    while True:
        k = secrets.randbelow(q - 1) + 1
        r = pow(a, k, p) % q
        if r == 0:
            continue
        s = (k * e + x * r) % q
        if s == 0:
            continue
        break

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"{r} {s}\n")
    print(f"Подпись записана в {out_path}")
    print(f"r={r}, s={s}")
    verify_input = "verify_input.txt"
    with open(in_path, "r", encoding="utf-8") as fin:
        message_text = fin.read()
    with open(verify_input, "w", encoding="utf-8") as f:
        f.write(f"{r} {s}\n{message_text}")
    print(f"Файл для проверки создан: {verify_input}")


def verify_file(in_path: str, params_path: str = DEFAULT_PARAMS_FILE):
    if not os.path.exists(PUBLIC_KEY_FILE):
        print("Ошибка: public.key не найден. Выполните keygen.")
        return
    with open(PUBLIC_KEY_FILE, "r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
        if len(lines) < 4:
            print("public.key должен содержать p, q, a, y (по одной строке).")
            return
        p = int(lines[0])
        q = int(lines[1])
        a = int(lines[2])
        y = int(lines[3])
    txt = open(in_path, "r", encoding="utf-8").read().splitlines()
    if not txt:
        print("in.txt пустой.")
        return
    sig_line = txt[0].strip()
    try:
        r_str, s_str = sig_line.split()
        r = int(r_str)
        s = int(s_str)
    except Exception:
        print("Неверный формат подписи в первой строке in.txt. Ожидается 'r s'.")
        return
    message = ""
    if len(txt) > 1:
        message = "\n".join(txt[1:])
    msg_bytes = message.encode("utf-8")
    e = hash_to_int(msg_bytes, q)
    if e == 0:
        e = 1
    if not (0 < r < q and 0 < s < q):
        result = "INVALID"
    else:
        try:
            v = modinv(e, q)
        except Exception:
            result = "INVALID"
        else:
            z1 = (s * v) % q
            z2 = ((q - r) * v) % q
            u = (pow(a, z1, p) * pow(y, z2, p)) % p
            u = u % q
            result = "VALID" if u == r else "INVALID"
    print(f"Проверка: {result}")


def usage():
    print("Использование:")
    print("  python lab6.py keygen")
    print("  python lab6.py sign in.txt out.txt")
    print("  python lab6.py verify verify_input.txt")
    print("")
    print("Формат params.txt (опционально): p=<число> q=<число> a=<число>")
    print("Формат in.txt для verify: первая строка 'r s', начиная со 2-й — сообщение.")


def lab6():
    if len(sys.argv) < 2:
        usage()
        return

    cmd = sys.argv[1]

    if cmd == "keygen":
        params_path = sys.argv[2] if len(sys.argv) >= 3 else DEFAULT_PARAMS_FILE
        keygen(params_path)

    elif cmd == "sign":
        if len(sys.argv) != 4:
            usage()
            return
        sign_file(sys.argv[2], sys.argv[3])

    elif cmd == "verify":
        if len(sys.argv) < 3:
            usage()
            return
        verify_file(sys.argv[2])

    else:
        usage()