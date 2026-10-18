# ⏱️ Python Timer Pro

Aplikasi penghitung waktu (Timer, Stopwatch, dan Pomodoro) modern, elegan, dan lengkap yang dibangun menggunakan bahasa pemrograman **Python murni** (Standard Library). Tidak memerlukan instalasi paket tambahan (`pip install`), langsung jalan di Windows!

---

## ✨ Fitur Utama

### 1. ⏳ Countdown Timer (Hitung Mundur)
- **Visual Circular Progress Gauge**: Indikator progress lingkaran dinamis dan modern dengan persentase sisa waktu.
- **Preset Cepat**: Tombol sekali klik untuk menambah waktu: `+1m`, `+3m`, `+5m`, `+10m`, `+15m`, `+30m`.
- **Pengaturan Waktu Fleksibel**: Input jam, menit, dan detik sesuai keinginan.
- **Alarm Suara Windows**: Melodi alarm yang ceria saat waktu habis menggunakan modul bawaan `winsound` di background thread (UI tidak macet/freeze).

### 2. ⏱️ Stopwatch Presisi
- **Akurasi Milidetik**: Format waktu detail `00:00:00.00`.
- **Pencatatan Putaran (Lap History)**: Rekam waktu split / putaran dengan tabel riwayat lap, durasi lap, dan total waktu akumulasi.
- Kontrol cepat: **Start**, **Pause/Resume**, **Lap**, dan **Reset**.

### 3. 🍅 Pomodoro Focus Timer
- **Teknik Pomodoro Produktivitas**:
  - 🎯 **Sesi Fokus**: 25 Menit kerja penuh konsentrasi.
  - ☕ **Istirahat Singkat**: 5 Menit rehat.
  - 🌴 **Istirahat Panjang**: 15 Menit setelah menyelesaikan 4 siklus fokus.
- **Pelacak Siklus Interaktif**: Menampilkan indikator titik visual `● ● ○ ○ (2 / 4)`.
- Notifikasi otomatis saat waktu fokus/istirahat berakhir.

### 4. 💻 Mode Terminal Interaktif (CLI)
- Tersedia versi CLI interaktif (`cli_timer.py`) dengan progress bar ASCII berwarna, cocok untuk penggunaan cepat di Command Prompt / PowerShell.

---

## 📁 Struktur Project

```
c:/timerpython/
│
├── main.py            # Aplikasi Desktop Utama (Tkinter Dark Mode High-DPI)
├── cli_timer.py       # Aplikasi Timer versi Terminal / CLI
├── sound_alert.py     # Modul efek suara & melodi alarm (Winsound Threaded)
├── run.bat            # Double-click launcher untuk membuka aplikasi GUI
├── run_cli.bat        # Double-click launcher untuk membuka versi Terminal
└── README.md          # Panduan dan dokumentasi lengkap
```

---

## 🚀 Cara Menjalankan

### Cara 1: Menggunakan File Batch (Paling Praktis)
- Cukup klik dua kali (double-click) pada file **`run.bat`** untuk membuka aplikasi GUI.
- Atau klik dua kali pada file **`run_cli.bat`** untuk membuka versi terminal.

### Cara 2: Lewat Command Prompt / PowerShell
Buka terminal di folder project, lalu jalankan:

1. **Menjalankan GUI Desktop**:
   ```bash
   python main.py
   ```

2. **Menjalankan Terminal CLI**:
   ```bash
   python cli_timer.py
   ```

---

## ⚙️ Kebutuhan Sistem

- **Python 3.8+** (Sudah teruji di Python 3.13)
- **Windows OS** (Untuk dukungan audio `winsound`)
- **Zero External Dependencies** (Menggunakan modul bawaan Python: `tkinter`, `time`, `threading`, `winsound`, `math`).
