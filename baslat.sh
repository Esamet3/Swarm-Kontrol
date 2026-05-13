#!/bin/bash

echo "Milli Swarm Kontrol Merkezi Başlatılıyor..."
echo "1. Adım: Gazebo Simülasyonu açılıyor..."

# Yeni bir terminal sekmesinde Gazebo'yu başlat
gnome-terminal --tab --title="Gazebo" -- bash -c "gazebo dron_and_rover.sdf; exec bash"

# Gazebo'nun kendine gelmesi için 5 saniye bekle
sleep 5

echo "2. Adım: Dron (SITL) başlatılıyor..."
gnome-terminal --tab --title="Dron SITL" -- bash -c "sim_vehicle.py -v ArduCopter -f gazebo-iris -I0; exec bash"

echo "3. Adım: Rover (SITL) başlatılıyor..."
gnome-terminal --tab --title="Rover SITL" -- bash -c "sim_vehicle.py -v Rover -f gazebo-rover -I1; exec bash"

# Araçların ağa bağlanması için 8 saniye bekle
echo "Sistemlerin hazır olması bekleniyor..."
sleep 8

echo "4. Adım: Kontrol Arayüzü açılıyor..."
python3 merkez_kontrol.py

