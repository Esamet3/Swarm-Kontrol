#!/bin/bash

# Proje dizinine geç ve tam yolu al (Başkaları da çalıştırabilsin diye)
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)

echo "Milli Swarm Kontrol Merkezi Başlatılıyor..."
echo "1. Adım: Gazebo Simülasyonu açılıyor..."

# Yeni bir terminal sekmesinde Gazebo'yu başlat (kendi klasörümüzdeki dron_and_rover.sdf'yi kullanarak)
gnome-terminal --tab --title="Gazebo" -- bash -ic "gz sim -v 4 -r \"${PROJECT_DIR}/dron_and_rover.sdf\"; exec bash"

# Gazebo'nun kendine gelmesi için 5 saniye bekle
sleep 5

echo "2. Adım: Dron (SITL) başlatılıyor..."
gnome-terminal --tab --title="Dron SITL" -- bash -ic "sim_vehicle.py -v ArduCopter -f gazebo-iris --model JSON --map --console -I 0 -w; exec bash"

echo "3. Adım: Rover (SITL) başlatılıyor..."
gnome-terminal --tab --title="Rover SITL" -- bash -ic "sim_vehicle.py -v Rover -f gazebo-rover --model JSON --map --console -I 1 -w; exec bash"

# Araçların ağa bağlanması için 8 saniye bekle
echo "Sistemlerin hazır olması bekleniyor..."
sleep 8

echo "4. Adım: Kontrol Arayüzü açılıyor..."
python3 merkez_kontrol.py

