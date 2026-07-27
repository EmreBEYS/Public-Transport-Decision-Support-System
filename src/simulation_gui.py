import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
import random
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Basit simülasyon verileri (örnek)
DURAK_SAYISI = 5
OTOBUS_SAYISI = 3

def simulasyon_adimi(otobusler, duraklar, dakika, durak_bekleme_suresi):
    loglar = []
    for durak in duraklar:
        degisim = random.randint(-2, 3)
        durak["yolcu"] = max(0, durak["yolcu"] + degisim)
        loglar.append(f"Dakika {dakika}: Durak <{durak['id']}> yolcu değişimi: {degisim}, toplam: {durak['yolcu']}")
    
    for otobus in otobusler:
        if otobus["bekleme_suresi"] > 0:
            otobus["bekleme_suresi"] -= 1
            continue
            
        onceki_konum = otobus["konum"]
        otobus["konum"] = (otobus["konum"] + 1) % len(duraklar)
        aktif_durak = duraklar[otobus["konum"]]
        inen = min(otobus["yolcu"], random.randint(0, 3))
        otobus["yolcu"] -= inen
        binen = min(aktif_durak["yolcu"], random.randint(0, 5))
        otobus["yolcu"] += binen
        aktif_durak["yolcu"] -= binen
        
        # Durakta bekleme süresi
        otobus["bekleme_suresi"] = durak_bekleme_suresi
        
        loglar.append(
            f"Dakika {dakika}: Otobüs {otobus['id']} {otobus['ikon']} "
            f"{onceki_konum}→{otobus['konum']} Durak <{aktif_durak['id']}>: "
            f"{inen} yolcu indi, {binen} yolcu bindi. Otobüste: {otobus['yolcu']} yolcu, Durakta: {aktif_durak['yolcu']}"
        )
    return loglar

class SimulasyonGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Otobüs Simülasyonu")
        self.root.geometry("1200x800")

        # Ana frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Sol panel (simülasyon ve durum paneli)
        self.left_panel = ttk.Frame(self.main_frame)
        self.left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Sağ panel (loglar ve grafikler)
        self.right_panel = ttk.Frame(self.main_frame)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Kontrol paneli
        self.kontrol_frame = ttk.LabelFrame(self.left_panel, text="Simülasyon Kontrolleri")
        self.kontrol_frame.pack(fill=tk.X, padx=5, pady=5)

        # Kontrol butonları
        self.kontrol_butonlar_frame = ttk.Frame(self.kontrol_frame)
        self.kontrol_butonlar_frame.pack(fill=tk.X, padx=5, pady=5)

        # Başlat/Durdur/Devam Et butonları
        self.baslat_btn = ttk.Button(self.kontrol_butonlar_frame, text="▶️ Simülasyonu Başlat", command=self.simulasyonu_baslat)
        self.baslat_btn.pack(side=tk.LEFT, padx=5)
        
        self.durdur_btn = ttk.Button(self.kontrol_butonlar_frame, text="⏸️ Simülasyonu Duraklat", command=self.simulasyonu_duraklat, state="disabled")
        self.durdur_btn.pack(side=tk.LEFT, padx=5)
        
        self.devam_btn = ttk.Button(self.kontrol_butonlar_frame, text="⏯️ Devam Et", command=self.simulasyonu_devam_et, state="disabled")
        self.devam_btn.pack(side=tk.LEFT, padx=5)
        
        self.sifirla_btn = ttk.Button(self.kontrol_butonlar_frame, text="🔄 Sıfırla", command=self.simulasyonu_sifirla, state="disabled")
        self.sifirla_btn.pack(side=tk.LEFT, padx=5)

        # Hız kontrolü
        self.hiz_frame = ttk.Frame(self.kontrol_frame)
        self.hiz_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(self.hiz_frame, text="Simülasyon Hızı (sn):").pack(side=tk.LEFT)
        self.hiz_var = tk.DoubleVar(value=1.0)
        self.hiz_scale = ttk.Scale(self.hiz_frame, from_=0.1, to=5.0, variable=self.hiz_var, orient=tk.HORIZONTAL)
        self.hiz_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.hiz_label = ttk.Label(self.hiz_frame, text="1.0")
        self.hiz_label.pack(side=tk.LEFT)
        self.hiz_scale.config(command=self.hiz_guncelle)

        # Durak bekleme süresi kontrolü
        self.bekleme_frame = ttk.Frame(self.kontrol_frame)
        self.bekleme_frame.pack(fill=tk.X, padx=5, pady=2)
        ttk.Label(self.bekleme_frame, text="Durak Bekleme Süresi (sn):").pack(side=tk.LEFT)
        self.bekleme_var = tk.IntVar(value=2)
        self.bekleme_scale = ttk.Scale(self.bekleme_frame, from_=1, to=10, variable=self.bekleme_var, orient=tk.HORIZONTAL)
        self.bekleme_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.bekleme_label = ttk.Label(self.bekleme_frame, text="2")
        self.bekleme_label.pack(side=tk.LEFT)
        self.bekleme_scale.config(command=self.bekleme_guncelle)

        # Durum paneli
        self.durum_frame = ttk.LabelFrame(self.left_panel, text="Simülasyon Durumu")
        self.durum_frame.pack(fill=tk.X, padx=5, pady=5)

        # Durum bilgileri için grid
        self.durum_labels = {}
        self.durum_values = {}
        
        # Genel durum bilgileri
        self.durum_labels["dakika"] = ttk.Label(self.durum_frame, text="Dakika:")
        self.durum_labels["dakika"].grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.durum_values["dakika"] = ttk.Label(self.durum_frame, text="0")
        self.durum_values["dakika"].grid(row=0, column=1, sticky="w", padx=5, pady=2)

        self.durum_labels["ozel_gun"] = ttk.Label(self.durum_frame, text="Özel Gün:")
        self.durum_labels["ozel_gun"].grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.durum_values["ozel_gun"] = ttk.Label(self.durum_frame, text="Hayır")
        self.durum_values["ozel_gun"].grid(row=1, column=1, sticky="w", padx=5, pady=2)

        self.durum_labels["aktif_hat"] = ttk.Label(self.durum_frame, text="Aktif Hat:")
        self.durum_labels["aktif_hat"].grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.durum_values["aktif_hat"] = ttk.Label(self.durum_frame, text="1")
        self.durum_values["aktif_hat"].grid(row=2, column=1, sticky="w", padx=5, pady=2)

        # Durak durumları için expandable frame
        self.durak_frame = ttk.LabelFrame(self.left_panel, text="Durak Durumları")
        self.durak_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Otobüs durumları için expandable frame
        self.otobus_frame = ttk.LabelFrame(self.left_panel, text="Otobüs Durumları")
        self.otobus_frame.pack(fill=tk.X, padx=5, pady=5)

        # Üstte sekmeler: Loglar ve Grafikler
        self.notebook = ttk.Notebook(self.right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Log sekmesi
        self.log_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.log_frame, text="Loglar")
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Grafik sekmesi
        self.grafik_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.grafik_frame, text="Grafikler")

        # Matplotlib figürleri
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(7, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.grafik_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Simülasyon paneli (otobüsler, duraklar, yolcular)
        self.simulasyon_panel = tk.Canvas(self.left_panel, bg="white", height=350)
        self.simulasyon_panel.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Simülasyon kontrol değişkenleri
        self.simulasyon_aktif = False
        self.simulasyon_duraklatildi = False
        self.sim_thread = None

        # Simülasyon verileri
        self.otobusler = [{"id": i+1, "konum": 0, "yolcu": random.randint(0, 10), "ikon": random.choice(["🚌", "🚐", "🚍"]), "bekleme_suresi": 0} for i in range(OTOBUS_SAYISI)]
        self.duraklar = [{"id": i+1, "yolcu": random.randint(0, 20)} for i in range(DURAK_SAYISI)]

        # Grafik için veri depoları
        self.durak_yolcu_log = [[] for _ in range(DURAK_SAYISI)]
        self.otobus_yolcu_log = [[] for _ in range(OTOBUS_SAYISI)]
        self.dakika_log = []

        # Thread ile GUI güncellemeleri arasında mesaj iletimi için
        self.log_queue = []
        self.dakika = 0

        # Durak ve otobüs durumlarını başlat
        self.durak_durumlarini_guncelle()
        self.otobus_durumlarini_guncelle()

        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.pencereyi_kapat)

    def hiz_guncelle(self, value):
        self.hiz_label.config(text=f"{float(value):.1f}")

    def bekleme_guncelle(self, value):
        self.bekleme_label.config(text=str(int(float(value))))

    def durak_durumlarini_guncelle(self):
        # Önceki widget'ları temizle
        for widget in self.durak_frame.winfo_children():
            widget.destroy()

        # Her durak için durum bilgilerini göster
        for i, durak in enumerate(self.duraklar):
            frame = ttk.Frame(self.durak_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"Durak {durak['id']}:").pack(side=tk.LEFT)
            ttk.Label(frame, text=f"Yolcu: {durak['yolcu']}").pack(side=tk.LEFT, padx=10)

    def otobus_durumlarini_guncelle(self):
        # Önceki widget'ları temizle
        for widget in self.otobus_frame.winfo_children():
            widget.destroy()

        # Her otobüs için durum bilgilerini göster
        for otobus in self.otobusler:
            frame = ttk.Frame(self.otobus_frame)
            frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(frame, text=f"{otobus['ikon']} Otobüs {otobus['id']}:").pack(side=tk.LEFT)
            ttk.Label(frame, text=f"Konum: {otobus['konum']}").pack(side=tk.LEFT, padx=10)
            ttk.Label(frame, text=f"Yolcu: {otobus['yolcu']}").pack(side=tk.LEFT, padx=10)
            if otobus["bekleme_suresi"] > 0:
                ttk.Label(frame, text=f"Bekleme: {otobus['bekleme_suresi']}sn").pack(side=tk.LEFT, padx=10)

    def durum_guncelle(self, dakika, ozel_gun, aktif_hat):
        self.durum_values["dakika"].config(text=str(dakika))
        self.durum_values["ozel_gun"].config(text="Evet" if ozel_gun else "Hayır")
        self.durum_values["aktif_hat"].config(text=str(aktif_hat))
        self.durak_durumlarini_guncelle()
        self.otobus_durumlarini_guncelle()

    def log_yaz(self, mesaj):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, mesaj + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def simulasyonu_baslat(self):
        if not self.simulasyon_aktif:
            self.simulasyon_aktif = True
            self.simulasyon_duraklatildi = False
            self.baslat_btn.config(state="disabled")
            self.durdur_btn.config(state="normal")
            self.devam_btn.config(state="disabled")
            self.sifirla_btn.config(state="normal")
            
            # Veri depolarını sıfırla
            self.durak_yolcu_log = [[] for _ in range(DURAK_SAYISI)]
            self.otobus_yolcu_log = [[] for _ in range(OTOBUS_SAYISI)]
            self.dakika_log = []
            self.dakika = 0
            self.log_queue = []
            
            # Logları temizle
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            
            # Grafikleri temizle
            self.ax1.clear()
            self.ax2.clear()
            self.canvas.draw()
            
            self.sim_thread = threading.Thread(target=self.simulasyon_dongusu, daemon=True)
            self.sim_thread.start()
            self.log_yaz("Simülasyon başlatıldı.")
            self.root.after(100, self.gui_guncelle)

    def simulasyonu_duraklat(self):
        if self.simulasyon_aktif and not self.simulasyon_duraklatildi:
            self.simulasyon_duraklatildi = True
            self.durdur_btn.config(state="disabled")
            self.devam_btn.config(state="normal")
            self.log_yaz("Simülasyon duraklatıldı.")

    def simulasyonu_devam_et(self):
        if self.simulasyon_aktif and self.simulasyon_duraklatildi:
            self.simulasyon_duraklatildi = False
            self.durdur_btn.config(state="normal")
            self.devam_btn.config(state="disabled")
            self.log_yaz("Simülasyon devam ediyor.")

    def simulasyonu_sifirla(self):
        if self.simulasyon_aktif:
            self.simulasyon_aktif = False
            self.simulasyon_duraklatildi = False
            self.baslat_btn.config(state="normal")
            self.durdur_btn.config(state="disabled")
            self.devam_btn.config(state="disabled")
            self.sifirla_btn.config(state="disabled")
            self.log_yaz("Simülasyon sıfırlandı.")

    def simulasyon_dongusu(self):
        while self.simulasyon_aktif and self.dakika < 100:
            if self.simulasyon_duraklatildi:
                time.sleep(0.1)  # Duraklatıldığında CPU kullanımını azalt
                continue
                
            ozel_gun = random.random() < 0.3  # %30 ihtimalle özel gün
            loglar = simulasyon_adimi(self.otobusler, self.duraklar, self.dakika, self.bekleme_var.get())
            
            # Logları ve verileri güncelle
            for log in loglar:
                self.log_queue.append(log)
            
            # Durak ve otobüs verilerini güncelle
            for i, durak in enumerate(self.duraklar):
                self.durak_yolcu_log[i].append(durak["yolcu"])
            for i, otobus in enumerate(self.otobusler):
                self.otobus_yolcu_log[i].append(otobus["yolcu"])
            self.dakika_log.append(self.dakika)
            
            # Durum panelini güncelle
            self.root.after(0, lambda: self.durum_guncelle(self.dakika, ozel_gun, 1))
            
            self.dakika += 1
            time.sleep(self.hiz_var.get())
        
        self.simulasyon_aktif = False
        self.root.after(0, self.simulasyonu_sifirla)

    def gui_guncelle(self):
        if not self.simulasyon_aktif:
            return
            
        # Logları ekle
        while self.log_queue:
            self.log_yaz(self.log_queue.pop(0))
        
        # Görsel ve grafik güncelle
        self.gorsel_guncelle()
        self.grafik_guncelle()
        
        # Simülasyon devam ediyorsa tekrar çağır
        self.root.after(100, self.gui_guncelle)

    def gorsel_guncelle(self):
        self.simulasyon_panel.delete("all")
        panel_w = self.simulasyon_panel.winfo_width()
        panel_h = self.simulasyon_panel.winfo_height()
        # Durakları yatayda sırala
        dx = panel_w // (DURAK_SAYISI + 1)
        dy = panel_h // 2

        for i, durak in enumerate(self.duraklar):
            x = dx * (i+1)
            # Durak: <>
            self.simulasyon_panel.create_text(x, dy, text=f"<{durak['id']}>", font=("Arial", 18, "bold"))
            # Duraktaki yolcular: *
            yolcu_str = "*" * min(durak["yolcu"], 20)
            self.simulasyon_panel.create_text(x, dy+30, text=yolcu_str, font=("Arial", 14), fill="blue")

        # Otobüsleri çiz
        # Önce her durakta kaç otobüs olduğunu say
        durak_otobus_sayisi = {}
        for otobus in self.otobusler:
            durak_otobus_sayisi[otobus["konum"]] = durak_otobus_sayisi.get(otobus["konum"], 0) + 1

        # Her durak için otobüsleri çiz
        for durak_konum in range(DURAK_SAYISI):
            otobusler_durakta = [o for o in self.otobusler if o["konum"] == durak_konum]
            for i, otobus in enumerate(otobusler_durakta):
                x = dx * (durak_konum+1)
                # Otobüsleri dikeyde dağıt
                y_offset = -40 - (i * 40)  # Her otobüs için 40 piksel aşağı
                self.simulasyon_panel.create_text(x, dy+y_offset, text=f"{otobus['ikon']} {otobus['id']}", font=("Arial", 18))
                yolcu_str = "*" * min(otobus["yolcu"], 20)
                self.simulasyon_panel.create_text(x, dy+y_offset-30, text=yolcu_str, font=("Arial", 14), fill="green")
                if otobus["bekleme_suresi"] > 0:
                    self.simulasyon_panel.create_text(x, dy+y_offset+20, text=f"⏳{otobus['bekleme_suresi']}", font=("Arial", 12), fill="red")

    def grafik_guncelle(self):
        self.ax1.clear()
        self.ax2.clear()
        
        # Durak yolcu grafiği
        for i, log in enumerate(self.durak_yolcu_log):
            if log:  # Sadece veri varsa çiz
                self.ax1.plot(self.dakika_log, log, label=f"Durak {i+1}", marker='o', markersize=3)
        self.ax1.set_title("Durak Yolcu Sayısı")
        self.ax1.set_xlabel("Dakika")
        self.ax1.set_ylabel("Yolcu")
        self.ax1.grid(True)
        self.ax1.legend()

        # Otobüs yolcu grafiği
        for i, log in enumerate(self.otobus_yolcu_log):
            if log:  # Sadece veri varsa çiz
                self.ax2.plot(self.dakika_log, log, label=f"Otobüs {i+1}", marker='o', markersize=3)
        self.ax2.set_title("Otobüs Yolcu Sayısı")
        self.ax2.set_xlabel("Dakika")
        self.ax2.set_ylabel("Yolcu")
        self.ax2.grid(True)
        self.ax2.legend()

        self.fig.tight_layout()
        self.canvas.draw()

    def pencereyi_kapat(self):
        if self.simulasyon_aktif:
            if messagebox.askokcancel("Çıkış", "Simülasyon devam ediyor. Çıkmak istediğinizden emin misiniz?"):
                self.simulasyon_aktif = False
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = SimulasyonGUI()
    gui.run()
