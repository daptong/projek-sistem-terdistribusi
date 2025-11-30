# Proyek Sistem Otomasi Rumah Pintar Berbasis Protokol MQTT

Anggota Kelompok:
1. Alif Putra Roy - 256150100111011
2. Aryo Bagus Kusumadewa Tutuko - 256150100111019
3. Muhammad Daffa Firmansyah - 256150100111010 

---

## Pendahuluan
Proyek ini adalah sistem untuk membuat rumah menjadi **Rumah Pintar** menggunakan protokol komunikasi ringan bernama **MQTT (*Message Queuing Telemetry Transport*)**.

Tujuan utamanya adalah memungkinkan pengguna untuk mengontrol dan memantau perangkat rumah dari jarak jauh, hanya melalui koneksi internet.

Proyek ini mensimulasikan 5 sensor virtual: sensor suhu, kelembaban, gerak, cahaya dan pintu

---

## Tujuan

Tujuan dari pengembangan sistem ini adalah:
1. **Implementasi Protokol MQTT**: Membangun sistem komunikasi *publish-subscribe* yang ringan dan responsif
2. **Monitoring Real-Time**: Menyediakan *dashboard visual* untuk memantau kondisi rumah (suhu, kelembaban, keamanan) tanpa delay yang signifikan
3. **Keandalan Data**: Menerapkan mekanisme *4-way handshake* untuk memastikan setiap data yang dikirim berhasil diterima dan diproses

---

## Batasan Masalah (Constraints)

Agar pengembangan tetap terfokus, proyek ini memiliki batasan sebagai berikut:
* **Lingkungan Simulasi**: Sistem dijalankan secara lokal (*localhost*) dna tidak menggunakan perangkat keras fisik (seperti Arduino/ESP32)
* **Sensor Virtual**: Data sensor (suhu, kelembaban, gerak, cahaya, pintu) dibuat menggunakan simulasi kode Python
* **Protokol**: Fokus utama adalah penggunaan protokol MQTT (Mosquitto) dan HTTP hanya digunakan untuk *serving* halaman *web dashboard*
* **Skala**: Sistem disimulasikan untuk satu unit rumah dengan 5 jenis sensor

---

## Motivasi

MQTT dipilih karena sangat efisien, menjadikannya pilihan ideal untuk perangkat IoT:

* **Efisiensi Protokol:** Model *publish/subscribe* MQTT yang bersifat asinkron menghilangkan kebutuhan *polling* terus menerus. Hal ini secara signifikan mengurangi *traffic* jaringan dan memperpanjang masa baterai pada sensor dengan sumber daya terbatas.

* **Penyederhanaan Integrasi:** MQTT (*Message Queuing Telemetry Transport*) menyediakan protokol komunikasi mesin-ke-mesin yang ringan menggunakan arsitektur *publish/subscribe* dengan broker, sehingga menyederhanakan integrasi perangkat dan pertukaran data asinkron.

* **Infrastruktur Modern:** Platform rumah pintar modern memanfaatkan **broker MQTT berbasis *cloud*** untuk menyediakan infrastruktur yang aman, andal, dan berbiaya rendah untuk otomasi jarak jauh. 

---

## Gambaran Umum

* **publisher.py:**
Kode ini mensimulasikan lima sensor secara virtual yaitu suhu, kelembaban, gerakan, cahaya dan pintu. Setiap sensor secara periodik mem-publish pesan JSON ke topik seperti `home/livingroom/temperature` dan mendengarkan *acknowledgement* pada topik `ack/<sensor_id>`
* **dashboard_complete.py:**
Kode ini merupakan *subscriber* ke topik sensor, dan juga mengirim pesan *acknowledgement* kembali ke setiap sensor. *Dashboard* ini menggunakan framework Flask untuk membangun aplikasi website.

---

## Desain dan Arsitektur Sistem
### Desain

* **Broker:**
*Broker* MQTT yang digunakan adalah Mosquitto dengan fungsi untuk menangani pesan yang dikirim dari *publisher* dan *subscriber*.
* **Struktur Topik:**
    -  Data Sensor: `home/<room>/<sensor>` (contoh: `home/livingroom/temperature`)
    - *Acknowledgement*: `ack/<sensor-id>` (contoh: `ack/livingroom-temperature-abc123`)
* **Alur Pesan:**
    1. `publisher` ke `broker` (*publish* data sensor)
    2. `broker` ke `subsciber` (*dashboard* (sebagai *subscriber*) menerima pesan)
    3. `subscriber` ke `broker` (*dashboard* mem-*publish* `ack` ke `ack/<sensor-id>`)
    4. `broker` ke `publisher` (*publisher* menerima `ack`)

### Arsitektur
Sistem terdiri dari 3 komponen utama:
1. **Broker** (Mosquitto): Pusat pertukaran pesan antar perangkat
2. **Publisher** (`publisher.py`): Mensimulasikan sensor yang mengirim data JSON ke broker secara periodik
3. **Subscriber** (`dashboard_complete.py`): Web Dashboard berbasis Flask yang menerima data, menampilkannya dalam grafik, dan mengirim balasan (ACK)

---

## Fitur Tambahan

* *Dashboard* menampilkan langsung data terbaru serta *timestamp* yang dikirimkan dari lima sensor.
Terdapat juga `Event Monitoring` yang menunjukkan peristiwa terstruktur dengan arah, sehingga pembaca dapat melacak pesan yang dikirim.

* Data sensor diperbarui secara otomatis tanpa *refresh* halaman (menggunakan *Server-Sent Events*/SSE)

* Sistem juga menggunakan mekanisme ACK *custom* untuk memastikan data sampai (*end to end*)

---

## Getting Started

1. Install dan Jalankan Broker MQTT Mosquitto
- Download Mosquitto dari https://mosquitto.org/download/ atau instal melalui Chocolatey: `choco install mosquitto`
- Jalankan broker menggunakan port default (1883)

```powershell
mosquitto -v
```

2. Install dependensi serta siapkan lingkungan Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Jalankan Dashboard (subsciber + web UI)

```powershell
python dashboard_complete.py --broker localhost --port 1883 --host 0.0.0.0 --webport 5000
# atau
python dashboard_complete.py --broker test.mosquitto.org --port 1883 --host 0.0.0.0 --webport 5000
```

4. Jalankan Publisher

```powershell
python publisher.py --broker localhost --port 1883
# atau
python publisher.py --broker test.mosquitto.org --port 1883
```

5. Buka web `http://localhost:5000` pada browser untuk melihat langsung aktivitas sensornya

---