import random
import time
import os
import matplotlib.pyplot as plt # type: ignore
from datetime import datetime
from logging import log_yaz # type: ignore
from graphics import yolcu_grafik_ciz, durak_doluluk_grafik
from simulation_gui import SimulasyonGUI
from simulation_menu import SimulasyonMenu
import tkinter as tk

# ------------------------
# Ortak Durum Sınıfı
# ------------------------
class DurumsalFaktorler:
    def __init__(self):
        self.durum = {}

    def guncelle(self):
        raise NotImplementedError

    def yazdir(self):
        for k, v in self.durum.items():
            print(f"{k}: {v}")

# GÜNCELLEME: Özel gün olasılığı rasgele belirlensin

def ozel_gun_var_mi():
    return random.random() < 0.3  # %30 ihtimalle özel gün

# ------------------------
# Hat ve Durak Sınıfları
# ------------------------
class Durak(DurumsalFaktorler):
    def __init__(self, durak_id):
        super().__init__()
        self.durak_id = durak_id
        self.yolcu_sayisi = 0
        self.engelli_yolcu = 0

    def guncelle(self, ozel_gun=False):
        toplam_yolcu = random.randint(0, 50)
        if ozel_gun:
            toplam_yolcu += random.randint(30, 60)
        engelli_oran = random.uniform(0.0, 0.2)
        self.engelli_yolcu = int(toplam_yolcu * engelli_oran)
        self.yolcu_sayisi = toplam_yolcu

        self.durum = {
            "durak_yogunlugu": self.yolcu_sayisi,
            "engelli_yolcu": self.engelli_yolcu,
            "hava": random.choice(["güneşli", "yağmurlu", "karlı"]),
            "yol_calismasi": random.choice([True, False]),
            "pazar_kurulmasi": random.choice([True, False]),
            "ozel_gun": ozel_gun,
            "toplu_tasima_aktif": random.choice([True, False])
        }

    def kontrol_et_ozel_durum(self):
        ayakta_yolcu = self.yolcu_sayisi - self.engelli_yolcu
        if self.engelli_yolcu >= 1 and ayakta_yolcu >= 4:
            print(f"⚠️ Durak {self.durak_id}: 1 engelli + 4 ayakta yolcu var.")
            return True
        return False

class Hat:
    def __init__(self, hat_id, durak_sayisi=5):
        self.hat_id = hat_id
        self.duraklar = [Durak(durak_id=i+1) for i in range(durak_sayisi)]

def yolcu_grafik_ciz(otobusler):
    print("[Grafik çizimi yapılmadı: yolcu_grafik_ciz()]")

def durak_doluluk_grafik(hat):
    print("[Grafik çizimi yapılmadı: durak_doluluk_grafik()]")

def kontrol_durumu_al():
    return False

# ------------------------
# Otobüs Sınıfları
# ------------------------
class Otobus(DurumsalFaktorler):
    def __init__(self, id, konum):
        super().__init__()
        self.id = id
        self.konum = konum
        self.kapasite = 30
        self.ic_yolcu = 0
        self.sefer_log = []
        self.sefer_suresi = 10
        self.ikon = "🚌"

    def guncelle(self, ozel_gun=False, dakika=0):
        katsayi = zaman_katsayisi(dakika)
        toplam_yolcu = int(random.randint(0, 50) * katsayi)
        if ozel_gun:
            toplam_yolcu = random.randint(40, 70)

        self.durum = {
            "ariza": random.choices([True, False], weights=[0.1, 0.9])[0],
            "doluluk": int((self.ic_yolcu / self.kapasite) * 100),
            "trafik": random.choice(["iyi", "orta", "kötü"]),
            "arkadan_gelen_arac_bos": random.choice([True, False]),
            "gercek_zamanli_kamera_yogunluk": toplam_yolcu
        }

    def yolcu_indir(self):
        if self.ic_yolcu > 0:
            oran = random.uniform(0.0, 1.0)
            inen = int(self.ic_yolcu * oran)
            self.ic_yolcu -= inen
            print(f"Otobüs {self.id}: {inen} yolcu indi.")

    def yolcu_al(self, normal_yolcu, engelli_yolcu):
        kalan_kapasite = self.kapasite - self.ic_yolcu
        engelli_birim = 4
        toplam_birim = normal_yolcu + (engelli_yolcu * engelli_birim)

        if toplam_birim <= kalan_kapasite:
            self.ic_yolcu += toplam_birim
            print(f"Otobüs {self.id}: {normal_yolcu} normal, {engelli_yolcu} engelli yolcu aldı.")
        else:
            max_engelli = min(engelli_yolcu, kalan_kapasite // engelli_birim)
            kalan_kapasite -= max_engelli * engelli_birim
            max_normal = min(normal_yolcu, kalan_kapasite)
            self.ic_yolcu += (max_normal + max_engelli * engelli_birim)
            print(f"Otobüs {self.id}: {max_normal} normal, {max_engelli} engelli yolcu aldı.")

    def logla(self, dakika):
        self.sefer_log.append((dakika, self.ic_yolcu))

    def hizlandir_sefer(self):
        self.sefer_suresi = max(5, self.sefer_suresi * 0.85)

class Otobus10m(Otobus):
    def __init__(self, id, konum):
        super().__init__(id, konum)
        self.kapasite = 30
        self.ikon = "🚐"

class Otobus12m(Otobus):
    def __init__(self, id, konum):
        super().__init__(id, konum)
        self.kapasite = 45
        self.ikon = "🚌"

class Otobus18m(Otobus):
    def __init__(self, id, konum):
        super().__init__(id, konum)
        self.kapasite = 70
        self.ikon = "🚍"

def rastgele_otobus_uret(id, konum):
    sinif = random.choice([Otobus10m, Otobus12m, Otobus18m])
    return sinif(id, konum)

# ------------------------
# Simülasyon Başlangıcı
# ------------------------
hatlar = [Hat(hat_id=i+1, durak_sayisi=5) for i in range(2)]
aktif_hat_index = 0
aktif_hat = hatlar[aktif_hat_index]
otobusler = [rastgele_otobus_uret(i+1, 0 if i < 3 else 4) for i in range(6)]

max_dakika = 10
dakika = 0

def zaman_katsayisi(dakika):
    saat = (dakika % 1440) // 60  # 1 gün = 1440 dakika
    if 7 <= saat < 9 or 17 <= saat < 19:
        return 1.8  # Yoğun saatler
    elif 9 <= saat < 17:
        return 1.2  # Normal saatler
    else:
        return 0.6  # Gece

while dakika < max_dakika:
    if kontrol_durumu_al():
        print("\n🛑 Simülasyon kullanıcı tarafından sonlandırıldı.")
        log_yaz("Simülasyon kullanıcı tarafından sonlandırıldı.")
        break

    ozel_gun = ozel_gun_var_mi()
    durum_bilgi = f"\n🕒 Dakika {dakika + 1} | {'🎉 Özel Gün' if ozel_gun else 'Normal Gün'} | Hat {aktif_hat.hat_id}"
    print(durum_bilgi)
    log_yaz(durum_bilgi)

    for durak in aktif_hat.duraklar:
        durak.guncelle(ozel_gun=ozel_gun)
        durak.kontrol_et_ozel_durum()

    for otobus in otobusler:
        otobus.guncelle(ozel_gun=ozel_gun)

    toplam_yolcu = sum(d.yolcu_sayisi for d in aktif_hat.duraklar)
    toplam_kapasite = sum(o.kapasite for o in otobusler)
    if ozel_gun and toplam_yolcu > toplam_kapasite:
        yeni_otobus_id = len(otobusler) + 1
        baslangic_konum = random.choice([0, 2, 4])
        yeni_otobus = rastgele_otobus_uret(yeni_otobus_id, baslangic_konum)
        otobusler.append(yeni_otobus)
        print(f"🆕 Ek Otobüs {yeni_otobus.id} ({type(yeni_otobus).__name__}) eklendi!")
        log_yaz(f"🆕 Ek Otobüs {yeni_otobus.id} ({type(yeni_otobus).__name__}) eklendi!")

    for i, otobus in enumerate(otobusler):
        aktif_durak = aktif_hat.duraklar[otobus.konum % len(aktif_hat.duraklar)]
        otobus.yolcu_indir()
        normal_yolcu = aktif_durak.yolcu_sayisi - aktif_durak.engelli_yolcu
        otobus.yolcu_al(normal_yolcu, aktif_durak.engelli_yolcu)
        otobus.logla(dakika)
        bilgi = f"{otobus.ikon} Otobüs {otobus.id} Konum: {otobus.konum} Yolcu: {otobus.ic_yolcu}/{otobus.kapasite}"
        print(bilgi)
        log_yaz(bilgi)

    if random.random() < 0.1:
        aktif_hat_index = (aktif_hat_index + 1) % len(hatlar)
        aktif_hat = hatlar[aktif_hat_index]
        print(f"🔁 Hat değiştirildi! Yeni hat: {aktif_hat.hat_id}")
        log_yaz(f"🔁 Hat değiştirildi! Yeni hat: {aktif_hat.hat_id}")

    dakika += 1
    time.sleep(1)

# Grafikler dış modülde çizilir
yolcu_grafik_ciz(otobusler)
durak_doluluk_grafik(aktif_hat)

if __name__ == "__main__":
    gui = SimulasyonGUI()
    gui.run()
