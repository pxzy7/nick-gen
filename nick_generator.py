import random
import string
import time
import requests
import threading
import os

# NOVAS FLAGS DE CONTROLE
is_generating = False
stop_flag = False
seen_nicks = set()
log_buffer = []

def generate_nick(length, first_letter="", charset="letters", use_underscore=False):
    if charset == "letters":
        chars = string.ascii_lowercase
    elif charset == "digits":
        chars = string.digits
    elif charset == "letters_digits":
        chars = string.ascii_lowercase + string.digits
    elif charset == "all":
        chars = string.ascii_letters + string.digits
    else:
        chars = string.ascii_lowercase

    if first_letter and first_letter != "0":
        base = first_letter.lower() + ''.join(random.choices(chars, k=length - 1))
    else:
        base = ''.join(random.choices(chars, k=length))

    if use_underscore and length > 1:
        index = random.randint(0, length - 1)
        if index < len(base) - 1:
            base = base[:index] + '_' + base[index + 1:]
        else:
            base = base[:index] + '_'

    return base

def check_minetools(nick):
    try:
        response = requests.get(f"https://api.minetools.eu/uuid/{nick}", timeout=5)
        data = response.json()
        return data.get("id") is None
    except Exception:
        return False

def check_mush(nick):
    try:
        response = requests.get(f"https://mush.com.br/api/player/{nick}")
        data = response.json()
        return not data.get("success", True) and data.get("error_code") == 404
    except Exception:
        return False

def generate_and_check_async(data):
    global is_generating, stop_flag, seen_nicks, log_buffer
    is_generating = True
    stop_flag = False
    seen_nicks = set()
    log_buffer = []

    length = int(data.get("length", 4))
    amount = int(data.get("amount", 5))
    first_letter = data.get("first_letter", "")
    charset = data.get("charset", "letters")
    use_underscore = data.get("underscore", False)

    generated = 0
    attempts = 0
    max_attempts = 1000

    output_file = {
        "letters": "valid_nicks_letters.txt",
        "digits": "valid_nicks_digits.txt",
        "letters_digits": "valid_nicks_letters_digits.txt",
        "all": "valid_nicks_all.txt"
    }.get(charset, "valid_nicks.txt")

    def log(text):
        print(text)
        log_buffer.append(text)

    def worker():
        nonlocal generated, attempts
        while generated < amount and attempts < max_attempts:
            attempts += 1
            nick = generate_nick(length, first_letter, charset, use_underscore)
            if nick in seen_nicks:
                continue
            seen_nicks.add(nick)

            minetools = check_minetools(nick)
            mush = check_mush(nick)

            log(f"Nick: {nick} | Minetools: {'✔️' if minetools else '❌'} | Mush: {'✔️' if mush else '❌'}")

            if minetools and mush:
                with open(output_file, "a") as f:
                    f.write(nick + "\n")
                generated += 1

            time.sleep(0.3)

    threads = [threading.Thread(target=worker) for _ in range(1)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    is_generating = False

def get_log_buffer():
    return "\n".join(log_buffer)

def get_latest_output_file():
    arquivos = [
        "valid_nicks_letters.txt",
        "valid_nicks_digits.txt",
        "valid_nicks_letters_digits.txt",
        "valid_nicks_all.txt"
    ]
    arquivos_existentes = [f for f in arquivos if os.path.exists(f)]
    if not arquivos_existentes:
        return "valid_nicks_letters.txt"  # fallback
    return max(arquivos_existentes, key=os.path.getmtime)

def generation_status():
    return is_generating
