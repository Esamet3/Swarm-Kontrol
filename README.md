# 🦅 Milli Swarm Kontrol Merkezi

![Platform](https://img.shields.io/badge/Platform-Ubuntu_20.04%20%7C%2022.04-orange.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Sim](https://img.shields.io/badge/Sim-Gazebo%2011-green.svg)

**Milli Swarm Kontrol Merkezi**, Gazebo 3D simülasyon ortamında ve ArduPilot (SITL) altyapısında çalışan İnsansız Hava Aracı (Dron) ve İnsansız Kara Aracının (Rover) eş zamanlı olarak kontrol edilmesini sağlayan modern bir Yer Kontrol İstasyonu (GCS) yazılımıdır.

Python ve **CustomTkinter** kullanılarak geliştirilen bu arayüz, birden fazla otonom sistemin (Sürü / Swarm) tek bir merkezden, klavye veya arayüz butonları aracılığıyla kolayca yönetilmesini hedefler.

## ✨ Öne Çıkan Özellikler
*   **Çoklu Araç Kontrolü:** Aynı anda hem quadcopter (Dron) hem de rover araçlarına komut gönderebilme.
*   **Gerçek Zamanlı Telemetri:** Her iki araç için anlık hız, irtifa ve uçuş/sürüş modu takibi.
*   **Modern Arayüz (Dark Mode):** Göz yormayan, modern CustomTkinter arayüz tasarımı.
*   **Tek Tıkla Simülasyon:** Tüm simülasyon altyapısını (Gazebo, Dron SITL, Rover SITL) tek bir betik (`baslat.sh`) ile saniyeler içinde başlatabilme.
*   **SITL Entegrasyonu:** Gerçek bir uçuş kontrolcüsünün yazılımsal ikizi olan ArduPilot SITL (Software In The Loop) teknolojisi ile %100 gerçekçi tepkiler.

---

## 🛠️ Sıfırdan Kurulum Rehberi (Ubuntu İçin)

Eğer bu projeyi başka, yepyeni bir bilgisayarda çalıştıracaksanız aşağıdaki adımları **sırasıyla** uygulayın.

### 0. Adım: Projeyi Bilgisayara İndirmek (Klonlamak)
Öncelikle terminali açın ve GitHub'daki kendi projenizi yeni bilgisayara indirin:
```bash
cd ~
git clone https://github.com/Esamet3/Swarm-Kontrol.git
```

### 1. Adım: Gazebo Simülatörünün Kurulması
Gazebo, ortamı ve araçları görselleştirecek 3 boyutlu simülatördür.
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
İndirdiğimiz projemizin klasörüne giriyoruz ve arayüz kütüphanelerini kuruyoruz:
```bash
cd ~/Swarm-Kontrol
pip install -r requirements.txt
```

---

## 🚀 Sistemi Çalıştırma

Tüm kurulumlar bittikten sonra projeyi tek tıkla ayağa kaldırmak için projenin olduğu klasörde terminali açın:
```bash
cd ~/Swarm-Kontrol
bash baslat.sh
```
*(Eğer baslat.sh yetki hatası verirse öncesinde `chmod +x baslat.sh` komutunu çalıştırabilirsiniz).*
