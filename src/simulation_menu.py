import tkinter as tk
from tkinter import ttk, messagebox
from simulation_gui import SimulasyonGUI

class SimulasyonMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Otobüs Simülasyon Kontrol Paneli")
        self.root.geometry("400x500")
        
        # Ana frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(self.main_frame, text="🚌 Otobüs Simülasyon Sistemi", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Simülasyon ayarları frame
        self.ayarlar_frame = ttk.LabelFrame(self.main_frame, text="Simülasyon Ayarları", padding="10")
        self.ayarlar_frame.pack(fill=tk.X, pady=10)
        
        # Durak sayısı ayarı
        self.durak_frame = ttk.Frame(self.ayarlar_frame)
        self.durak_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.durak_frame, text="Durak Sayısı:").pack(side=tk.LEFT)
        self.durak_sayisi = ttk.Spinbox(self.durak_frame, from_=3, to=10, width=5)
        self.durak_sayisi.set(5)
        self.durak_sayisi.pack(side=tk.LEFT, padx=5)
        
        # Otobüs sayısı ayarı
        self.otobus_frame = ttk.Frame(self.ayarlar_frame)
        self.otobus_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.otobus_frame, text="Otobüs Sayısı:").pack(side=tk.LEFT)
        self.otobus_sayisi = ttk.Spinbox(self.otobus_frame, from_=1, to=10, width=5)
        self.otobus_sayisi.set(3)
        self.otobus_sayisi.pack(side=tk.LEFT, padx=5)
        
        # Simülasyon süresi ayarı
        self.sure_frame = ttk.Frame(self.ayarlar_frame)
        self.sure_frame.pack(fill=tk.X, pady=5)
        ttk.Label(self.sure_frame, text="Simülasyon Süresi (dk):").pack(side=tk.LEFT)
        self.simulasyon_suresi = ttk.Spinbox(self.sure_frame, from_=10, to=100, width=5)
        self.simulasyon_suresi.set(60)
        self.simulasyon_suresi.pack(side=tk.LEFT, padx=5)
        
        # Kontrol butonları frame
        self.kontrol_frame = ttk.LabelFrame(self.main_frame, text="Simülasyon Kontrolleri", padding="10")
        self.kontrol_frame.pack(fill=tk.X, pady=10)
        
        # Başlat butonu
        self.baslat_btn = ttk.Button(self.kontrol_frame, text="▶️ Simülasyonu Başlat", 
                                    command=self.simulasyonu_baslat)
        self.baslat_btn.pack(fill=tk.X, pady=5)
        
        # Durdur butonu
        self.durdur_btn = ttk.Button(self.kontrol_frame, text="⏹️ Simülasyonu Durdur", 
                                    command=self.simulasyonu_durdur, state="disabled")
        self.durdur_btn.pack(fill=tk.X, pady=5)
        
        # Duraklat butonu
        self.duraklat_btn = ttk.Button(self.kontrol_frame, text="⏸️ Simülasyonu Duraklat", 
                                      command=self.simulasyonu_duraklat, state="disabled")
        self.duraklat_btn.pack(fill=tk.X, pady=5)
        
        # Devam et butonu
        self.devam_btn = ttk.Button(self.kontrol_frame, text="⏯️ Devam Et", 
                                   command=self.simulasyonu_devam_et, state="disabled")
        self.devam_btn.pack(fill=tk.X, pady=5)
        
        # Sıfırla butonu
        self.sifirla_btn = ttk.Button(self.kontrol_frame, text="🔄 Sıfırla", 
                                     command=self.simulasyonu_sifirla, state="disabled")
        self.sifirla_btn.pack(fill=tk.X, pady=5)
        
        # Durum bilgisi
        self.durum_frame = ttk.LabelFrame(self.main_frame, text="Durum Bilgisi", padding="10")
        self.durum_frame.pack(fill=tk.X, pady=10)
        
        self.durum_label = ttk.Label(self.durum_frame, text="Simülasyon hazır")
        self.durum_label.pack(fill=tk.X)
        
        # Simülasyon GUI referansı
        self.sim_gui = None
        
        # Pencere kapatma olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.pencereyi_kapat)

    def simulasyonu_baslat(self):
        try:
            # Simülasyon ayarlarını al
            durak_sayisi = int(self.durak_sayisi.get())
            otobus_sayisi = int(self.otobus_sayisi.get())
            simulasyon_suresi = int(self.simulasyon_suresi.get())
            
            # Simülasyon GUI'sini başlat
            self.sim_gui = SimulasyonGUI(durak_sayisi, otobus_sayisi, simulasyon_suresi)
            
            # Buton durumlarını güncelle
            self.baslat_btn.config(state="disabled")
            self.durdur_btn.config(state="normal")
            self.duraklat_btn.config(state="normal")
            self.sifirla_btn.config(state="normal")
            
            # Durum bilgisini güncelle
            self.durum_label.config(text="Simülasyon çalışıyor")
            
            # Simülasyonu başlat
            self.sim_gui.simulasyonu_baslat()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Simülasyon başlatılırken bir hata oluştu: {str(e)}")

    def simulasyonu_durdur(self):
        if self.sim_gui:
            self.sim_gui.simulasyonu_sifirla()
            self.durum_label.config(text="Simülasyon durduruldu")
            self.baslat_btn.config(state="normal")
            self.durdur_btn.config(state="disabled")
            self.duraklat_btn.config(state="disabled")
            self.devam_btn.config(state="disabled")
            self.sifirla_btn.config(state="disabled")

    def simulasyonu_duraklat(self):
        if self.sim_gui:
            self.sim_gui.simulasyonu_duraklat()
            self.durum_label.config(text="Simülasyon duraklatıldı")
            self.duraklat_btn.config(state="disabled")
            self.devam_btn.config(state="normal")

    def simulasyonu_devam_et(self):
        if self.sim_gui:
            self.sim_gui.simulasyonu_devam_et()
            self.durum_label.config(text="Simülasyon devam ediyor")
            self.duraklat_btn.config(state="normal")
            self.devam_btn.config(state="disabled")

    def simulasyonu_sifirla(self):
        if self.sim_gui:
            self.sim_gui.simulasyonu_sifirla()
            self.durum_label.config(text="Simülasyon sıfırlandı")
            self.baslat_btn.config(state="normal")
            self.durdur_btn.config(state="disabled")
            self.duraklat_btn.config(state="disabled")
            self.devam_btn.config(state="disabled")
            self.sifirla_btn.config(state="disabled")

    def pencereyi_kapat(self):
        if self.sim_gui and self.sim_gui.simulasyon_aktif:
            if messagebox.askokcancel("Çıkış", "Simülasyon devam ediyor. Çıkmak istediğinizden emin misiniz?"):
                self.simulasyonu_durdur()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    menu = SimulasyonMenu()
    menu.run()
