# Milli Swarm Kontrol Merkezi

Bu proje, Gazebo simülasyon ortamında ArduPilot (SITL) ile çalışan bir Dron ve Rover'ın tek bir Python arayüzünden (CustomTkinter) aynı anda kontrol edilmesini sağlar.

---

## 🛠️ Sıfırdan Kurulum Rehberi (Ubuntu İçin)

Eğer bu projeyi çalıştıracağınız bilgisayarda hiçbir şey kurulu değilse, aşağıdaki adımları **sırasıyla** terminalinize kopyalayıp yapıştırarak tüm sistemi kurabilirsiniz.

### 1. Adım: Gazebo Simülatörünün Kurulması
Gazebo, dron ve aracımızı göreceğimiz 3 boyutlu simülasyon dünyasıdır.
Terminali açın ve şu komutu yapıştırıp Enter'a basın:
```bash
sudo apt update
sudo apt install gazebo11 libgazebo11-dev -y
```

### 2. Adım: ArduPilot'un (Otopilot) Kurulması
ArduPilot, araçlarımızın beynidir (SITL). Kurulumu bilgisayar hızına göre 5-15 dakika sürebilir.
Terminale sırasıyla şu komutları yapıştırın:
```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive
Tools/environment_install/install-prereqs-ubuntu.sh -y
```
*(Bu işlem bittikten sonra terminali kapatıp **yeni bir terminal** açın ki ayarlar aktif olsun).*

### 3. Adım: Gazebo ve ArduPilot'u Birbirine Bağlayan Eklenti
ArduPilot'un Gazebo ile konuşabilmesi için bu eklentiyi kurmamız şart.
```bash
cd ~
git clone https://github.com/khancyr/ardupilot_gazebo.git
cd ardupilot_gazebo
mkdir build
cd build
cmake ..
make -j4
sudo make install
```

### 4. Adım: Python Kütüphanelerinin Kurulması
Şimdi bizim indirdiğimiz proje klasörünün içine terminalden girin ve arayüzümüz için gereken Python kütüphanelerini kurun:
```bash
pip install -r requirements.txt
```

---

## 🚀 Sistemi Çalıştırma

Tüm kurulumlar bittikten sonra (veya bilgisayarınızda bunlar zaten kuruluysa), sistemi tek tıkla ayağa kaldırmak çok kolaydır!

Projenin ana dizininde (yani bu dosyanın olduğu klasörde) terminali açın ve sadece şu komutu yazın:
```bash
bash baslat.sh
```

**Not:** Bu komut arka planda otomatik olarak yeni pencereler açıp Gazebo'yu, Dron'u ve Rover'ı başlatacak, en son da Kontrol Arayüzünü karşınıza getirecektir.



