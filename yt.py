
import os
import json
import threading
import time
import shutil
import subprocess
from utils.color import *
from yt_dlp import YoutubeDL
from pathlib import Path

os.system('clear')  # Untuk Linux dan MacOS
# os.system('cls')  # Untuk Windows

cols, _ = shutil.get_terminal_size()
CONFIG_FILE = "utils/config.json"
URL_HISTORY_FILE = "utils/url_history.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"download_folder": os.getcwd()}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_url_history():
    if not os.path.exists(URL_HISTORY_FILE):
        return []
    with open(URL_HISTORY_FILE, "r") as f:
        return json.load(f)

def save_url_history(history):
    with open(URL_HISTORY_FILE, "w") as f:
        json.dump(history, f)

def get_download_folder(config):
    return config.get("download_folder", os.getcwd())

def select_folder():
    folder = input(f"{putih}[{hijau}+{putih}] {putih}Masukkan path folder untuk menyimpan musik {kuning}({cyan}default: folder ini{kuning}){ungu}: {hijau}").strip()
    if not folder:
        folder = os.getcwd()
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder
# download video YouTube 
def download_video(url, folder, url_history):
    # Pastikan folder tujuan ada
    os.makedirs(folder, exist_ok=True)

    # Konfigurasi default YoutubeDL
    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'quiet': True,
        'merge_output_format': 'mp4',  # Pastikan output akhir adalah MP4
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            # Filter format MP4
            mp4_formats = [
                f for f in formats
                if f.get('ext') == 'mp4' and f.get('vcodec') != 'none' and f.get('filesize')
            ]

            # Jika tidak ada format MP4, gunakan format lain
            if not mp4_formats:
                print(f"{kuning}[{merah}!{kuning}] {merah}Format MP4 tidak tersedia. Menampilkan format lain yang tersedia:")
                available_formats = [
                    f for f in formats if f.get('vcodec') != 'none' and f.get('filesize')
                ]
                if not available_formats:
                    print(f"{kuning}[{merah}!{kuning}] {merah}Tidak ada format video dengan informasi ukuran yang tersedia.")
                    return

                # Tampilkan format lain
                for idx, f in enumerate(available_formats):
                    size_mb = f['filesize'] / (1024 * 1024)  # Konversi ke MB
                    print(f"{putih}[{hijau}{idx}{putih}]{kosong} Resolusi: {merah}{f.get('height', 'N/A')}p{kosong}, Format: {merah}{f.get('ext', 'N/A')}{kosong}, Ukuran: {merah}{size_mb:.2f}{kosong} MB")
                
                pilihan = input(f"[{hijau}>{kosong}] Pilih resolusi (nomor){ungu}: {cyan}").strip()
                try:
                    pilihan = int(pilihan)
                    selected_format = available_formats[pilihan]
                    ydl_opts['format'] = selected_format['format_id']
                except (ValueError, IndexError):
                    print(f"{kuning}[{merah}!{kuning}] {merah}Pilihan tidak valid!")
                    return

                # Unduh format selain MP4
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    original_file = os.path.join(folder, f"{info['title']}.{selected_format['ext']}")
                    converted_file = os.path.join(folder, f"{info['title']}.mp4")
                    
                    # Konversi ke MP4 menggunakan ffmpeg
                    print(f"[{hijau}#{kosong}] Mengonversi file ke format MP4...")
                    subprocess.run([
                        "ffmpeg", "-i", original_file, "-c:v", "libx264", "-c:a", "aac", "-strict", "experimental", converted_file,
                        "-y"  # Overwrite file jika sudah ada
                    ])
                    print(f"[{hijau}#{kosong}] File berhasil dikonversi ke MP4: {converted_file}")
            else:
                # Tampilkan format MP4 yang tersedia
                print(f"[{hijau}#{kosong}] Resolusi MP4 yang tersedia untuk video ini:")
                for idx, f in enumerate(mp4_formats):
                    size_mb = f['filesize'] / (1024 * 1024)  # Konversi ukuran ke MB
                    print(f"[{hijau}{idx}{kosong}] Resolusi: {merah}{f.get('height', 'N/A')}p{kosong}, Ukuran: {merah}{size_mb:.2f}{kosong} MB")
                
                pilihan = input(f"[{hijau}>{kosong}] Pilih resolusi (nomor): {cyan}").strip()
                try:
                    pilihan = int(pilihan)
                    selected_format = mp4_formats[pilihan]
                    ydl_opts['format'] = f"{selected_format['format_id']}+bestaudio/best"
                except (ValueError, IndexError):
                    print(f"{kuning}[{merah}!{kuning}] {merah}Pilihan tidak valid!")
                    return
                
                # Unduh MP4
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    file_path = os.path.join(folder, f"{info['title']}.mp4")
                    print(f"[{hijau}#{kosong}] Download selesai! Video disimpan di: {hijau}{file_path}{kosong}")

            # Simpan riwayat URL
            url_history.append(url)
            save_url_history(url_history)

    except Exception as e:
        print(f"{kuning}[{merah}!{kuning}] {kuning}Terjadi kesalahan: {merah}{e}{kosong}")

def loading_animation(stop_event):
    # Animasi loading dinamis
    symbols = ['/', '-', '\\', '|']
    idx = 0
    while not stop_event.is_set():
        print(f"\r{putih}loading {putih}[{hijau}{symbols[idx]}{putih}]{kosong}", end="", flush=True)
        idx = (idx + 1) % len(symbols)
        time.sleep(0.1)
    print(f"\r{cyan}loading {putih}[{hijau}✓{putih}] {hijau}Selesai!{kosong}", end="", flush=True)
def download_audio(url, folder, url_history):
    # Fungsi untuk mendownload audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'quiet': True,
    }

    if url in url_history:
        print(f"{kuning}[{merah}#{kuning}] {merah}URL ini sudah pernah diunduh sebelumnya.{kosong}")
        confirm = input(f"{kuning}[{merah}>{kuning}] {merah}Apakah Anda ingin mendownload ulang? (y/n): {cyan}").strip().lower()
        if confirm != 'y':
            return

    # Animasi loading
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    loading_thread.start()

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_name = f"{cyan}{info['title']}.{kuning}mp3{kosong}"
        print(f"\n{kuning}[{putih}#{kuning}] {cyan}Download selesai! File '{kuning}{file_name}{cyan}' disimpan di '{merah}{folder}{cyan}'.{kosong}\n\n")
        url_history.append(url)
        save_url_history(url_history)
    except Exception as e:
        print(f"{kuning}[{merah}!{kuning}]{putih} Terjadi kesalahan{ungu}: {merah}{e}{kosong}\n\n")
    finally:
        stop_event.set()
        loading_thread.join()

def list_downloaded_files(folder):
    # Menampilkan daftar file musik (.mp3) dan video (.mp4) yang sudah diunduh.
    music_files = [f for f in os.listdir(folder) if f.endswith(".mp3")]
    video_files = [f for f in os.listdir(folder) if f.endswith(".mp4")]

    if music_files or video_files:
        print(f"{putih}[{hijau}#{putih}] File yang tersedia di folder unduhan {ungu}:{kosong}")
        
        if music_files:
            print(f"\n{kuning}--- Musik (.mp3) ---{kosong}")
            for idx, file in enumerate(music_files, start=1):
                print(f"   {putih}[{hijau}{idx}{putih}] {kosong}{file}")
        else:
            print(f"\n{kuning}--- Musik (.mp3) ---{kosong}")
            print(f"{kuning}[{merah}#{kuning}] {merah}Tidak ada musik yang ditemukan.{kosong}")

        if video_files:
            print(f"\n{kuning}--- Video (.mp4) ---{kosong}")
            for idx, file in enumerate(video_files, start=1):
                print(f"   {putih}[{hijau}{len(music_files) + idx}{putih}] {kosong}{file}")
        else:
            print(f"\n{kuning}--- Video (.mp4) ---{kosong}")
            print(f"{kuning}[{merah}#{kuning}] {merah}Tidak ada video yang ditemukan.{kosong}")
    else:
        print(f"{kuning}[{merah}#{kuning}] {merah}Tidak ada file yang ditemukan di folder unduhan.{kosong}")

def main():
    config = load_config()
    url_history = load_url_history()
    download_folder = get_download_folder(config)

    while True:
        
        print(f"\n{cyan}+------------------------------------+")
        print("|           YouTube  Downloader      |")
        print(f"+------------------------------------+{kosong}")

        print(f"{putih}[{hijau}#{putih}] Menu{ungu}:")
        print(f"   {putih}[{hijau}1{putih}] Download Musik")
        print(f"   {putih}[{hijau}2{putih}] Download Video")  # Tambahan
        print(f"   {putih}[{hijau}3{putih}] Daftar Diunduh")
        print(f"   {putih}[{hijau}4{putih}] Pengaturan")
        print(f"   {putih}[{hijau}0{putih}] Keluar{kosong}")

        pilihan = input(f"{putih}[{hijau}${putih}] Pilih opsi{ungu}: {cyan}").strip()

        if pilihan == "1":
            url = input(f"{putih}[{merah}>{putih}] {hijau}Masukkan URL YouTube: {cyan}").strip()
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows
            print(f'{hijau}-{kosong}' * cols)
            if not url:
                print(f"{putih}[{merah}!{putih}] {kuning}URL tidak boleh kosong!{kosong}")
                print(f'{hijau}-{kosong}' * cols)
                continue

            print(f"{putih}[{ungu}>{putih}] {putih}Sedang mendownload, harap tunggu...\033[0m")
            download_audio(url, download_folder, url_history)

        elif pilihan == "2":  # Tambahan
            url = input(f"{putih}[{merah}>{putih}] {hijau}Masukkan URL YouTube: {cyan}").strip()
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows
            print(f'{hijau}-{kosong}' * cols)
            if not url:
                print(f"{putih}[{merah}!{putih}] {kuning}URL tidak boleh kosong!{kosong}")
                print(f'{hijau}-{kosong}' * cols)
                continue

            print(f"{putih}[{ungu}>{putih}] {putih}Sedang mendownload video, harap tunggu...\033[0m")
            download_video(url, download_folder, url_history)
            


        elif pilihan == "3":
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows
            print(f'{hijau}-{kosong}' * cols)
            list_downloaded_files(download_folder)
            print(f'{hijau}-{kosong}' * cols)

        elif pilihan == "4":
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows
            print(f'{hijau}-{kosong}' * cols)
            print(f"{kuning}[{putih}#{kuning}] {putih}Pengaturan{ungu}:")
            print(f"   {kuning}[{cyan}1{kuning}] {kosong}Ganti Folder Unduhan")
            print(f"   {kuning}[{cyan}2{kuning}] {kosong}Reset ke Pengaturan Awal")
            print(f"   {kuning}[{cyan}3{kuning}] {kosong}Kembali ke Menu Utama{kosong}")

            sub_pilihan = input(f"{putih}[{hijau}>{putih}] Pilih opsi{ungu}: {cyan}").strip()

            if sub_pilihan == "1":
                os.system('clear')  # Untuk Linux dan MacOS
                # os.system('cls')  # Untuk Windows
                print(f'{hijau}-{kosong}' * cols)
                download_folder = select_folder()
                config['download_folder'] = download_folder
                save_config(config)
                os.system('clear')  # Untuk Linux dan MacOS
                # os.system('cls')  # Untuk Windows
                print(f'{hijau}-{kosong}' * cols)
                print(f"{kuning}[{putih}#{kuning}] {kosong}Folder unduhan berhasil diubah ke '{hijau}{download_folder}{kosong}'.")
                print(f'{hijau}-{kosong}' * cols)
            elif sub_pilihan == "2":
               
                config = {"download_folder": os.getcwd()}
                os.system('clear')  # Untuk Linux dan MacOS
                # os.system('cls')  # Untuk Windows
                print(f'{hijau}-{kosong}' * cols)
                save_config(config)
                url_history.clear()
                save_url_history(url_history)
                download_folder = os.getcwd()
                print(f" {kuning}[{putih}#{kuning}]{hijau} Pengaturan berhasil direset ke default.{kosong}")
                print(f'{hijau}-{kosong}' * cols)
            elif sub_pilihan == "3":
                os.system('clear')  # Untuk Linux dan MacOS
                # os.system('cls')  # Untuk Windows
                continue
            else:
              
                print(f"{kunging}[{merah}!{kuning}] {merah}Pilihan tidak valid. Silakan coba lagi!{kosong}")

        elif pilihan == "0":
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows
            print(f"{kuning}[{hijau}#{kuning}] {merah}Keluar.{kosong} Sampai jumpa!")
            break

        else:
            print(f"{kuning}[{merah}!{kuning}] {kosong}Pilihan tidak valid. Silakan coba lagi!")
            os.system('clear')  # Untuk Linux dan MacOS
            # os.system('cls')  # Untuk Windows

if __name__ == "__main__":
    main()

