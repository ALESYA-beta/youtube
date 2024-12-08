# YouTube Downloader

YouTube Downloader adalah aplikasi berbasis Python untuk mengunduh video atau audio dari YouTube dengan opsi untuk memilih format dan resolusi. Aplikasi ini mendukung konversi otomatis ke format MP4 atau MP3 dan menyediakan antarmuka terminal yang ramah pengguna.

## Fitur Utama
1. **Download Video**  
   - Pilih resolusi dan format video yang diinginkan.
   - Unduhan otomatis disimpan dalam format MP4.
2. **Download Audio**  
   - Mendukung konversi audio dari video ke MP3 dengan kualitas tinggi (320kbps).
3. **Daftar File yang Diunduh**  
   - Tampilkan semua file yang telah diunduh di folder target.
4. **Pengaturan Folder Unduhan**  
   - Ganti folder unduhan sesuai keinginan.
   - Reset pengaturan ke default.
5. **Riwayat URL**  
   - Hindari pengunduhan ulang untuk URL yang sama dengan sistem riwayat unduhan.

## Cara Kerja
- **Konfigurasi dan Riwayat**:  
  File konfigurasi (`config.json`) dan riwayat URL (`url_history.json`) disimpan di folder `utils`.  
- **Integrasi dengan `yt-dlp`**:  
  Memanfaatkan pustaka `yt-dlp` untuk mendownload video/audio dari YouTube.
- **Konversi Format**:  
  Jika format yang diunduh bukan MP4, file akan dikonversi menggunakan `ffmpeg`.

## Instalasi
1. Pastikan Anda telah menginstal Python (>=3.8).
2. Clone repositori ini:
   ```bash
   git clone https://github.com/ALESYA-beta/youtube.git
3. **Instal dependensi:**
    - langsung saja `bash install.sh`


    
  
