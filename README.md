# Milli Swarm Kontrol Merkezi

Bu proje, Gazebo simülasyon ortamında ArduPilot (SITL) ile çalışan bir Dron ve Rover'ın tek bir Python arayüzünden (CustomTkinter) aynı anda kontrol edilmesini sağlar.

---

## 🛠️ Sıfırdan Kurulum Rehberi (Ubuntu İçin)

Eğer bu projeyi başka, yepyeni bir bilgisayarda çalıştıracaksanız aşağıdaki adımları **sırasıyla** uygulayın.

### 0. Adım: Projeyi Bilgisayara İndirmek (Klonlamak)
Öncelikle terminali açın ve GitHub'daki kendi projenizi yeni bilgisayara indirin:
```bash
cd ~
git clone https://github.com/KULLANICI_ADIN/PROJE_ADIN.git
```
*(Yukarıdaki linki kendi deponuzun linkiyle değiştirmeyi unutmayın).*

### 1. Adım: Gazebo Simülatörünün Kurulması
Gazebo, ortamı ve araçları görselleştirecek simülatördür.
```bash
sudo apt update
sudo apt install gazebo11 libgazebo11-dev -y
```

### 2. Adım: ArduPilot'un (Otopilot) Kurulması
ArduPilot, araçlarımızın beynidir (SITL). Kurulumu bilgisayar hızına göre 5-15 dakika sürebilir.
```bash
cd ~
git clone https://github.com/ArduPilot/ardupilot.git
cd ardupilot
git submodule update --init --recursive
Tools/environment_install/install-prereqs-ubuntu.sh -y
```
**ÇOK ÖNEMLİ:** Kurulum bittikten sonra `sim_vehicle.py` komutunun sistem tarafından tanınması için **terminali kapatıp baştan açın** veya şu komutu çalıştırın:
```bash
source ~/.profile
```

### 3. Adım: Gazebo ve ArduPilot Eklentisinin Kurulması
Gazebo'nun ArduPilot ile haberleşmesi için bu eklenti şarttır.
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
**ÇOK ÖNEMLİ (Modellerin Tanıtılması):** Simülatörün dron ve rover modellerini bulabilmesi için şu yolları sisteme eklemeliyiz. Terminale sırasıyla yapıştırın:
```bash
echo 'export GAZEBO_MODEL_PATH=~/ardupilot_gazebo/models:${GAZEBO_MODEL_PATH}' >> ~/.bashrc
echo 'export GAZEBO_PLUGIN_PATH=/usr/lib/x86_64-linux-gnu/gazebo-11/plugins:/usr/local/lib:${GAZEBO_PLUGIN_PATH}' >> ~/.bashrc
source ~/.bashrc
```

### 4. Adım: Python Kütüphanelerinin Kurulması
İndirdiğimiz kendi projemizin klasörüne giriyoruz ve arayüz kütüphanelerini kuruyoruz:
```bash
cd ~/PROJE_ADIN
pip install -r requirements.txt
```

---

## 🚀 Sistemi Çalıştırma

Tüm kurulumlar bittikten sonra projeyi tek tıkla ayağa kaldırmak için projenin olduğu klasörde terminali açın:
```bash
bash baslat.sh
```
*(Eğer baslat.sh yetki hatası verirse öncesinde `chmod +x baslat.sh` komutunu çalıştırabilirsiniz).*
