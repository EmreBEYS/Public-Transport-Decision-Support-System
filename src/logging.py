from datetime import datetime

def log_yaz(mesaj):
    zaman_damgasi = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("simulasyon_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{zaman_damgasi}] {mesaj}\n")
