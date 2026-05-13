import time
import threading
import collections
import collections.abc
import customtkinter as ctk

# DroneKit yaması
collections.MutableMapping = collections.abc.MutableMapping
from dronekit import connect, VehicleMode

# ==========================================
# GLOBAL DEĞİŞKENLER
# ==========================================
dron = None
rover = None
aktif_sekme = "Dron"
dron_hiz_carpani = 100      # PWM sapması (0-500 arası)
rover_hiz_carpani = 100     # PWM sapması (0-500 arası)
rover_trim = 0              # Direksiyon kanalı (CH1) için ince ayar
basili_tuslar = set()       # Şu an basılı olan yön tuşları

# ==========================================
# 1. BAĞLANTI VE BAŞLATMA FONKSİYONLARI
# ==========================================

def dron_baslat():
    global dron
    try:
        durum_guncelle("Dron'a bağlanılıyor...", "dron")
        # Simülasyon kasılmalarına karşı zaman aşımı (timeout) sürelerini 60 saniyeye çıkardık
        dron = connect('udp:127.0.0.1:14550', wait_ready=True, timeout=60, heartbeat_timeout=60)

        # Güvenlik kilitlerini kaldır
        dron.parameters['ARMING_CHECK'] = 0
        dron.parameters['FRAME_CLASS'] = 1
        dron.parameters['FRAME_TYPE'] = 1

        # Hız limitleri (cm/s)
        try:
            dron.parameters['WPNAV_LOIT_SPEED'] = 2000
            dron.parameters['WPNAV_SPEED'] = 2000
        except:
            pass

        time.sleep(1)

        dron.mode = VehicleMode("GUIDED")
        while dron.mode.name != 'GUIDED':
            time.sleep(0.5)

        dron.armed = True
        while not dron.armed:
            time.sleep(0.5)

        durum_guncelle("Havalanıyor (10 m)...", "dron")
        dron.simple_takeoff(10)

        while True:
            alt = dron.location.global_relative_frame.alt
            if alt is not None and alt >= 10 * 0.95:
                dron.mode = VehicleMode("LOITER")
                durum_guncelle("Hazır — LOITER modunda ✓", "dron")
                break
            time.sleep(1)

    except Exception as e:
        durum_guncelle(f"HATA: {e}", "dron")


def rover_baslat():
    global rover
    try:
        durum_guncelle("Rover'a bağlanılıyor...", "rover")
        rover = connect('udp:127.0.0.1:14560', wait_ready=True)

        rover.parameters['ARMING_CHECK'] = 0
        try:
            rover.parameters['CRUISE_SPEED'] = 10
            rover.parameters['CRUISE_THROTTLE'] = 50
            
            # SİHİRLİ DOKUNUŞ: ArduPilot'a bu aracın Skid-Steer (Tank) olduğunu söylüyoruz.
            # Böylece CH1(Yön) ve CH3(Gaz) komutlarını alıp Sol ve Sağ motorlara kendi miksleyip dağıtacak.
            rover.parameters['SERVO1_FUNCTION'] = 73  # 73: Sol Motor (Throttle Left)
            rover.parameters['SERVO3_FUNCTION'] = 74  # 74: Sağ Motor (Throttle Right)
            
            # Not: Eğer ileri bastığınızda araç kendi etrafında dönüyorsa, motorlardan biri ters bağlanmış demektir.
            # O durumda ilgili motorun REVERSED parametresini 1 yapmamız gerekir.
        except:
            pass

        time.sleep(1)

        # ACRO modu: channel override tam çalışır
        # MANUAL modda override çalışmaz veya sınırlı çalışır
        rover.mode = VehicleMode("ACRO")
        while rover.mode.name != 'ACRO':
            time.sleep(0.5)

        rover.armed = True
        while not rover.armed:
            time.sleep(0.5)

        durum_guncelle("Hazır — ACRO modunda ✓", "rover")

    except Exception as e:
        durum_guncelle(f"HATA: {e}", "rover")


# ==========================================
# 2. MOTOR KONTROL DÖNGÜSÜ (Arka plan thread)
# ==========================================
# ArduPilot Rover override kanalları:
#   CH1 = Direksiyon (steer): 1000=tam sol | 1500=düz | 2000=tam sağ
#   CH3 = Gaz (throttle):     1000=tam geri | 1500=dur  | 2000=tam ileri
# Firmware, skid-steer diferansiyelini CH1+CH3'ten otomatik hesaplar.
# Siz sadece "nereye gitmek istiyorum" bilgisini gönderin.

def motor_kontrol_dongusu():
    while True:
        # --- DRON (LOITER modunda RC override) ---
        # CH1=Roll, CH2=Pitch, CH3=Throttle, CH4=Yaw
        d_roll     = 1500
        d_pitch    = 1500
        d_throttle = 1500
        d_yaw      = 1500

        # --- ROVER (ACRO modunda CH1=steer, CH3=throttle) ---
        r_steer    = 1500
        r_throttle = 1500

        if aktif_sekme == "Dron":
            if 'w' in basili_tuslar: d_pitch    = 1500 - dron_hiz_carpani  # İleri
            if 's' in basili_tuslar: d_pitch    = 1500 + dron_hiz_carpani  # Geri
            if 'a' in basili_tuslar: d_roll     = 1500 - dron_hiz_carpani  # Sol
            if 'd' in basili_tuslar: d_roll     = 1500 + dron_hiz_carpani  # Sağ
            if 'q' in basili_tuslar: d_throttle = 1500 + dron_hiz_carpani  # Yüksel
            if 'e' in basili_tuslar: d_throttle = 1500 - dron_hiz_carpani  # Alçal

        elif aktif_sekme == "Rover":
            # Temel ileri/geri → CH3 (gaz)
            if 'w' in basili_tuslar: r_throttle = 1500 + rover_hiz_carpani
            if 's' in basili_tuslar: r_throttle = 1500 - rover_hiz_carpani

            # Dönüş → CH1 (direksiyon); firmware sol/sağ motoru ayarlar
            if 'a' in basili_tuslar: r_steer = 1500 - rover_hiz_carpani
            if 'd' in basili_tuslar: r_steer = 1500 + rover_hiz_carpani

            # Trim sadece direksiyon kanalına eklenir
            r_steer += rover_trim

        # PWM sınırları (güvenlik)
        d_roll     = max(1000, min(2000, d_roll))
        d_pitch    = max(1000, min(2000, d_pitch))
        d_throttle = max(1000, min(2000, d_throttle))
        d_yaw      = max(1000, min(2000, d_yaw))
        r_steer    = max(1000, min(2000, r_steer))
        r_throttle = max(1000, min(2000, r_throttle))

        # Dron — LOITER modunda override gönder
        if dron is not None and dron.mode.name == "LOITER":
            dron.channels.overrides = {
                '1': d_roll,
                '2': d_pitch,
                '3': d_throttle,
                '4': d_yaw
            }

        # Rover — arm edilmişse override gönder
        if rover is not None and rover.armed:
            rover.channels.overrides = {
                '1': r_steer,    # Direksiyon
                '3': r_throttle  # Gaz
            }

        time.sleep(0.05)  # 20 Hz


# ==========================================
# 3. TELEMETRİ DÖNGÜSÜ (GUI thread)
# ==========================================

def telemetri_guncelle():
    if dron is not None:
        try:
            alt = dron.location.global_relative_frame.alt
            if alt is not None:
                lbl_dron_alt.configure(text=f"{alt:.1f} m")

            if dron.velocity is not None:
                hiz = (dron.velocity[0]**2 + dron.velocity[1]**2 + dron.velocity[2]**2) ** 0.5
                lbl_dron_hiz.configure(text=f"{hiz:.1f} m/s")

            mod = dron.mode.name if dron.mode else "—"
            lbl_dron_mod.configure(text=mod)
        except:
            pass

    if rover is not None:
        try:
            r_hiz = rover.groundspeed
            if r_hiz is not None:
                lbl_rover_hiz.configure(text=f"{r_hiz:.1f} m/s")

            mod = rover.mode.name if rover.mode else "—"
            lbl_rover_mod.configure(text=mod)
        except:
            pass

    app.after(500, telemetri_guncelle)


# ==========================================
# 4. YARDIMCI FONKSİYONLAR
# ==========================================

def durum_guncelle(mesaj, arac):
    """Durum etiketini GUI thread-safe şekilde günceller."""
    def _guncelle():
        if arac == "dron":
            lbl_dron_durum.configure(text=mesaj)
        else:
            lbl_rover_durum.configure(text=mesaj)
    app.after(0, _guncelle)


def sekme_degisti():
    global aktif_sekme
    aktif_sekme = tabview.get()
    basili_tuslar.clear()  # Sekme geçişinde takılı kalan tuşları temizle


def dron_hiz_ayarla():
    global dron_hiz_carpani
    try:
        val = max(0, min(100, int(ent_dron_hiz.get())))
        dron_hiz_carpani = int((val / 100.0) * 500)
        lbl_dron_hiz_gosterge.configure(text=f"Hız katsayısı: {val}%")
    except:
        pass


def rover_hiz_ayarla():
    global rover_hiz_carpani
    try:
        val = max(0, min(100, int(ent_rover_hiz.get())))
        rover_hiz_carpani = int((val / 100.0) * 500)
        lbl_rover_hiz_gosterge.configure(text=f"Hız katsayısı: {val}%")
    except:
        pass


def rover_trim_ayarla(deger):
    global rover_trim
    rover_trim = int(float(deger))
    lbl_trim_gosterge.configure(text=f"Direksiyon trimi: {rover_trim:+d}")


def sabit_kal():
    """Tüm tuşları bırakır, araçlar nötr PWM alır ve yerinde durur."""
    basili_tuslar.clear()


def acil_inis_fren():
    """Dron iner, rover durur."""
    basili_tuslar.clear()
    if dron is not None:
        try:
            dron.mode = VehicleMode("LAND")
            dron.channels.overrides = {}
        except:
            pass
    if rover is not None:
        try:
            rover.channels.overrides = {'1': 1500, '3': 1500}
        except:
            pass
    durum_guncelle("ACİL İNİŞ!", "dron")
    durum_guncelle("ACİL FREN!", "rover")


def buton_bas(key):
    basili_tuslar.add(key)


def buton_birak(key):
    basili_tuslar.discard(key)


def buton_bagla(btn, key):
    """Bir butonu basma/bırakma olaylarına bağlar."""
    btn.bind("<ButtonPress-1>",   lambda e, k=key: buton_bas(k))
    btn.bind("<ButtonRelease-1>", lambda e, k=key: buton_birak(k))
    btn.bind("<Leave>",           lambda e, k=key: buton_birak(k))


# ==========================================
# 5. ARAYÜZ (GUI)
# ==========================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.geometry("820x520")
app.title("Milli Swarm Kontrol Merkezi")
app.resizable(False, False)

# Ana grid: sol = sekmeler, sağ = telemetri
app.grid_columnconfigure(0, weight=3)
app.grid_columnconfigure(1, weight=1)
app.grid_rowconfigure(0, weight=1)

# ---- Sekme Görünümü ----
tabview = ctk.CTkTabview(app, command=sekme_degisti)
tabview.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="nsew")
tabview.add("Dron")
tabview.add("Rover")
aktif_sekme = tabview.get()


# ==== DRON SEKMESİ ====
dron_sekme = tabview.tab("Dron")
dron_sekme.grid_columnconfigure(0, weight=1)

# Başlat butonu
ctk.CTkButton(
    dron_sekme, text="🚁  Başlat ve Havalan", height=42,
    font=("Arial", 14, "bold"),
    command=lambda: threading.Thread(target=dron_baslat, daemon=True).start()
).pack(pady=(15, 4), padx=20, fill="x")

# Durum etiketi
lbl_dron_durum = ctk.CTkLabel(dron_sekme, text="Bağlı değil", font=("Arial", 11),
                               text_color="gray")
lbl_dron_durum.pack()

# Hız ayarı
dron_hiz_frame = ctk.CTkFrame(dron_sekme, fg_color="transparent")
dron_hiz_frame.pack(pady=(10, 2))
ctk.CTkLabel(dron_hiz_frame, text="Hız (0–100):", font=("Arial", 12)).pack(side="left", padx=(0, 5))
ent_dron_hiz = ctk.CTkEntry(dron_hiz_frame, placeholder_text="20", width=60)
ent_dron_hiz.pack(side="left", padx=4)
ctk.CTkButton(dron_hiz_frame, text="Uygula", width=70, command=dron_hiz_ayarla).pack(side="left")

lbl_dron_hiz_gosterge = ctk.CTkLabel(dron_sekme, text="Hız katsayısı: 20%",
                                      font=("Arial", 11), text_color="gray")
lbl_dron_hiz_gosterge.pack()

# Kontrol butonları (WASD + QE)
d_ctrl = ctk.CTkFrame(dron_sekme, fg_color="transparent")
d_ctrl.pack(pady=12)

BTN_W, BTN_H = 82, 52

btn_dq = ctk.CTkButton(d_ctrl, text="⬆ Yüksel", width=BTN_W, height=BTN_H)
btn_dq.grid(row=0, column=0, padx=4, pady=4)
btn_dw = ctk.CTkButton(d_ctrl, text="▲ İleri",  width=BTN_W, height=BTN_H)
btn_dw.grid(row=0, column=1, padx=4, pady=4)
btn_de = ctk.CTkButton(d_ctrl, text="⬇ Alçal", width=BTN_W, height=BTN_H)
btn_de.grid(row=0, column=2, padx=4, pady=4)

btn_da = ctk.CTkButton(d_ctrl, text="◀ Sol",   width=BTN_W, height=BTN_H)
btn_da.grid(row=1, column=0, padx=4, pady=4)
btn_ds = ctk.CTkButton(d_ctrl, text="▼ Geri",  width=BTN_W, height=BTN_H)
btn_ds.grid(row=1, column=1, padx=4, pady=4)
btn_dd = ctk.CTkButton(d_ctrl, text="▶ Sağ",   width=BTN_W, height=BTN_H)
btn_dd.grid(row=1, column=2, padx=4, pady=4)

for btn, key in [(btn_dq,'q'), (btn_dw,'w'), (btn_de,'e'),
                 (btn_da,'a'), (btn_ds,'s'), (btn_dd,'d')]:
    buton_bagla(btn, key)


# ==== ROVER SEKMESİ ====
rover_sekme = tabview.tab("Rover")

# Başlat butonu
ctk.CTkButton(
    rover_sekme, text="🚗  Başlat ve Hazırla", height=42,
    font=("Arial", 14, "bold"),
    command=lambda: threading.Thread(target=rover_baslat, daemon=True).start()
).pack(pady=(15, 4), padx=20, fill="x")

# Durum etiketi
lbl_rover_durum = ctk.CTkLabel(rover_sekme, text="Bağlı değil", font=("Arial", 11),
                                text_color="gray")
lbl_rover_durum.pack()

# Hız ayarı
rover_hiz_frame = ctk.CTkFrame(rover_sekme, fg_color="transparent")
rover_hiz_frame.pack(pady=(10, 2))
ctk.CTkLabel(rover_hiz_frame, text="Hız (0–100):", font=("Arial", 12)).pack(side="left", padx=(0, 5))
ent_rover_hiz = ctk.CTkEntry(rover_hiz_frame, placeholder_text="20", width=60)
ent_rover_hiz.pack(side="left", padx=4)
ctk.CTkButton(rover_hiz_frame, text="Uygula", width=70, command=rover_hiz_ayarla).pack(side="left")

lbl_rover_hiz_gosterge = ctk.CTkLabel(rover_sekme, text="Hız katsayısı: 20%",
                                       font=("Arial", 11), text_color="gray")
lbl_rover_hiz_gosterge.pack()

# Trim (direksiyon ince ayarı) — sadece CH1'e etki eder
rover_trim_frame = ctk.CTkFrame(rover_sekme, fg_color="transparent")
rover_trim_frame.pack(pady=(6, 2))
lbl_trim_gosterge = ctk.CTkLabel(rover_trim_frame, text="Direksiyon trimi:  0",
                                  font=("Arial", 11))
lbl_trim_gosterge.pack(side="left", padx=(0, 10))
slider_trim = ctk.CTkSlider(rover_trim_frame, from_=-100, to=100,
                             width=160, command=rover_trim_ayarla)
slider_trim.set(0)
slider_trim.pack(side="left")

# Kontrol butonları (WASD)
r_ctrl = ctk.CTkFrame(rover_sekme, fg_color="transparent")
r_ctrl.pack(pady=12)

btn_rw = ctk.CTkButton(r_ctrl, text="▲ İleri", width=BTN_W, height=BTN_H)
btn_rw.grid(row=0, column=1, padx=4, pady=4)

btn_ra = ctk.CTkButton(r_ctrl, text="◀ Sol",  width=BTN_W, height=BTN_H)
btn_ra.grid(row=1, column=0, padx=4, pady=4)
btn_rs = ctk.CTkButton(r_ctrl, text="▼ Geri", width=BTN_W, height=BTN_H)
btn_rs.grid(row=1, column=1, padx=4, pady=4)
btn_rd = ctk.CTkButton(r_ctrl, text="▶ Sağ",  width=BTN_W, height=BTN_H)
btn_rd.grid(row=1, column=2, padx=4, pady=4)

for btn, key in [(btn_rw,'w'), (btn_ra,'a'), (btn_rs,'s'), (btn_rd,'d')]:
    buton_bagla(btn, key)


# ==== SAĞ PANEL — TELEMETRİ ====
sag = ctk.CTkFrame(app)
sag.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
sag.grid_rowconfigure(8, weight=1)  # Boşluğu alta iter

ctk.CTkLabel(sag, text="TELEMETRİ", font=("Arial", 16, "bold")).grid(
    row=0, column=0, pady=(14, 6), padx=12, sticky="ew")

# Dron
ctk.CTkLabel(sag, text="🚁 Dron", font=("Arial", 12, "bold"),
             text_color="#00CCAA").grid(row=1, column=0, padx=12, sticky="w")

ctk.CTkLabel(sag, text="Yükseklik", font=("Arial", 10),
             text_color="gray").grid(row=2, column=0, padx=12, sticky="w")
lbl_dron_alt = ctk.CTkLabel(sag, text="0.0 m", font=("Courier", 26, "bold"),
                              text_color="#00FFCC")
lbl_dron_alt.grid(row=3, column=0, padx=12, sticky="w")

ctk.CTkLabel(sag, text="Hız", font=("Arial", 10),
             text_color="gray").grid(row=4, column=0, padx=12, sticky="w")
lbl_dron_hiz = ctk.CTkLabel(sag, text="0.0 m/s", font=("Courier", 20, "bold"),
                              text_color="#00FFCC")
lbl_dron_hiz.grid(row=5, column=0, padx=12, sticky="w")

ctk.CTkLabel(sag, text="Mod", font=("Arial", 10),
             text_color="gray").grid(row=6, column=0, padx=12, sticky="w")
lbl_dron_mod = ctk.CTkLabel(sag, text="—", font=("Courier", 13),
                              text_color="#00FFCC")
lbl_dron_mod.grid(row=7, column=0, padx=12, sticky="w")

# Ayraç
ctk.CTkLabel(sag, text="─" * 18, text_color="gray",
             font=("Arial", 9)).grid(row=8, column=0, pady=6)

# Rover
ctk.CTkLabel(sag, text="🚗 Rover", font=("Arial", 12, "bold"),
             text_color="#FFAA00").grid(row=9, column=0, padx=12, sticky="w")

ctk.CTkLabel(sag, text="Hız", font=("Arial", 10),
             text_color="gray").grid(row=10, column=0, padx=12, sticky="w")
lbl_rover_hiz = ctk.CTkLabel(sag, text="0.0 m/s", font=("Courier", 20, "bold"),
                               text_color="#FFAA00")
lbl_rover_hiz.grid(row=11, column=0, padx=12, sticky="w")

ctk.CTkLabel(sag, text="Mod", font=("Arial", 10),
             text_color="gray").grid(row=12, column=0, padx=12, sticky="w")
lbl_rover_mod = ctk.CTkLabel(sag, text="—", font=("Courier", 13),
                               text_color="#FFAA00")
lbl_rover_mod.grid(row=13, column=0, padx=12, sticky="w")

# Boşluk doldurucu
ctk.CTkLabel(sag, text="").grid(row=14, column=0, sticky="nsew")
sag.grid_rowconfigure(14, weight=1)

# Kontrol butonları (alt)
ctk.CTkButton(
    sag, text="⏸  Sabit Kal / Dur",
    font=("Arial", 12, "bold"),
    fg_color="#E07000", hover_color="#B05500",
    height=44, command=sabit_kal
).grid(row=15, column=0, padx=10, pady=(0, 6), sticky="ew")

ctk.CTkButton(
    sag, text="🛑  Acil İniş / Fren",
    font=("Arial", 12, "bold"),
    fg_color="#CC2222", hover_color="#991111",
    height=44, command=acil_inis_fren
).grid(row=16, column=0, padx=10, pady=(0, 14), sticky="ew")


# ==========================================
# 6. DÖNGÜ BAŞLATMA
# ==========================================
telemetri_guncelle()
threading.Thread(target=motor_kontrol_dongusu, daemon=True).start()
app.mainloop()