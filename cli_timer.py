"""
cli_timer.py - Aplikasi Timer Interaktif berbasis Terminal (CLI)
Mendukung: Countdown Timer, Stopwatch (dengan Lap), dan Pomodoro Mode.
"""
import sys
import time
import os
import re
import sound_alert

# Kode warna ANSI untuk tampilan terminal yang menarik
class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    MAGENTA = "\033[95m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

# Aktifkan ANSI color support di Windows terminal
if os.name == 'nt':
    os.system('color')

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(f"""{Color.CYAN}{Color.BOLD}
  ╔════════════════════════════════════════════════════════════╗
  ║                ⏱️   PYTHON PRO TIMER CLI                   ║
  ║           Countdown • Stopwatch • Pomodoro Focus           ║
  ╚════════════════════════════════════════════════════════════╝{Color.RESET}""")

def parse_time_input(input_str: str) -> int:
    """
    Mengubah input seperti '10m', '1h30m', '90s', atau angka murni detik menjadi total detik.
    """
    input_str = input_str.strip().lower()
    if not input_str:
        return 0
    
    # Jika angka murni (dianggap detik atau menit)
    if input_str.isdigit():
        return int(input_str)
    
    total_seconds = 0
    # Pola jam (h/j), menit (m), detik (s/d)
    hours = re.search(r'(\d+)\s*(?:h|j|jam)', input_str)
    minutes = re.search(r'(\d+)\s*(?:m|menit)', input_str)
    seconds = re.search(r'(\d+)\s*(?:s|d|detik)', input_str)
    
    if hours:
        total_seconds += int(hours.group(1)) * 3600
    if minutes:
        total_seconds += int(minutes.group(1)) * 60
    if seconds:
        total_seconds += int(seconds.group(1))
    
    return total_seconds

def format_seconds(sec: int) -> str:
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"

def draw_progress_bar(percent: float, width: int = 30) -> str:
    filled_len = int(width * percent)
    bar = "█" * filled_len + "░" * (width - filled_len)
    return bar

def run_countdown(seconds: int, title: str = "COUNTDOWN"):
    if seconds <= 0:
        print(f"{Color.RED}Waktu harus lebih dari 0 detik!{Color.RESET}")
        time.sleep(1.5)
        return

    print(f"\n{Color.YELLOW}Memulai {title} selama {format_seconds(seconds)}... Tekan Ctrl+C untuk membatalkan.{Color.RESET}\n")
    sound_alert.play_start_sound()
    time.sleep(1)

    total = seconds
    try:
        while seconds >= 0:
            percent = 1.0 - (seconds / total)
            bar = draw_progress_bar(percent, width=32)
            time_str = format_seconds(seconds)
            pct_str = f"{int(percent * 100):3d}%"

            # Dynamic color based on remaining time
            if percent > 0.8:
                bar_color = Color.RED
            elif percent > 0.5:
                bar_color = Color.YELLOW
            else:
                bar_color = Color.CYAN

            sys.stdout.write(
                f"\r  {Color.BOLD}{Color.WHITE}[{time_str}]{Color.RESET} "
                f"{bar_color}[{bar}]{Color.RESET} {Color.BOLD}{pct_str}{Color.RESET} "
            )
            sys.stdout.flush()

            if seconds == 0:
                break
            time.sleep(1)
            seconds -= 1

        print(f"\n\n{Color.GREEN}{Color.BOLD}🎉 WAKTU HABIS! ({title}){Color.RESET}")
        sound_alert.play_alarm_finished(repeat=3)
        input(f"\n{Color.GRAY}Tekan Enter untuk kembali ke menu utama...{Color.RESET}")

    except KeyboardInterrupt:
        print(f"\n\n{Color.RED}⚠️  Timer dihentikan oleh pengguna.{Color.RESET}")
        time.sleep(1)

def run_stopwatch():
    print_banner()
    print(f"{Color.MAGENTA}{Color.BOLD}=== STOPWATCH ==={Color.RESET}")
    print(f"{Color.GRAY}Petunjuk: Tekan Enter untuk START, Enter lagi untuk LAP, atau Ctrl+C untuk SELESAI.{Color.RESET}\n")
    input(f"{Color.YELLOW}Tekan Enter untuk memulai Stopwatch...{Color.RESET}")
    
    sound_alert.play_start_sound()
    start_time = time.time()
    laps = []
    lap_start_time = start_time
    
    print("\n" + "="*45)
    print(f"{Color.GREEN}⏱️  Stopwatch Berjalan! Tekan Ctrl+C untuk berhenti.{Color.RESET}")
    print("="*45)

    import threading
    stop_event = threading.Event()
    lap_event = threading.Event()

    def display_loop():
        while not stop_event.is_set():
            now = time.time()
            elapsed = now - start_time
            m = int(elapsed // 60)
            s = int(elapsed % 60)
            ms = int((elapsed * 100) % 100)
            sys.stdout.write(f"\r  {Color.CYAN}{Color.BOLD}Waktu: {m:02d}:{s:02d}.{ms:02d}{Color.RESET}  | Putaran: {len(laps)} ")
            sys.stdout.flush()
            time.sleep(0.05)

    t = threading.Thread(target=display_loop, daemon=True)
    t.start()

    try:
        while True:
            # Menunggu input Enter untuk mencatat Lap
            val = input()
            lap_time = time.time()
            total_elapsed = lap_time - start_time
            lap_duration = lap_time - lap_start_time
            lap_start_time = lap_time

            laps.append((total_elapsed, lap_duration))
            sound_alert.play_lap_sound()

            m_tot = int(total_elapsed // 60)
            s_tot = int(total_elapsed % 60)
            ms_tot = int((total_elapsed * 100) % 100)

            m_lap = int(lap_duration // 60)
            s_lap = int(lap_duration % 60)
            ms_lap = int((lap_duration * 100) % 100)

            print(f"  🚩 Lap {len(laps):02d}: +{m_lap:02d}:{s_lap:02d}.{ms_lap:02d} (Total: {m_tot:02d}:{s_tot:02d}.{ms_tot:02d})")

    except KeyboardInterrupt:
        stop_event.set()
        total_time = time.time() - start_time
        sound_alert.play_pause_sound()
        print(f"\n\n{Color.YELLOW}{Color.BOLD}🛑 Stopwatch Dihentikan!{Color.RESET}")
        m = int(total_time // 60)
        s = int(total_time % 60)
        ms = int((total_time * 100) % 100)
        print(f"Total Waktu: {Color.BOLD}{m:02d}:{s:02d}.{ms:02d}{Color.RESET}")
        if laps:
            print(f"Total Putaran (Lap) Tercatat: {len(laps)}")
        input(f"\n{Color.GRAY}Tekan Enter untuk kembali ke menu utama...{Color.RESET}")

def run_pomodoro():
    print_banner()
    print(f"{Color.MAGENTA}{Color.BOLD}=== POMODORO FOCUS TIMER ==={Color.RESET}")
    print(f"{Color.GRAY}Standar Pomodoro: 25 menit Kerja Fokus, 5 menit Istirahat Singkat.{Color.RESET}")
    print(f"Setelah 4 sesi kerja, Anda berhak mendapatkan Istirahat Panjang (15 menit)!\n")

    sessions_target = 4
    for session in range(1, sessions_target + 1):
        print(f"\n{Color.CYAN}{Color.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}  SESI FOKUS {session}/{sessions_target} (25 Menit Kerja){Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Color.RESET}")
        input(f"{Color.YELLOW}Siap fokus? Tekan Enter untuk mulai sesi...{Color.RESET}")
        run_countdown(25 * 60, title=f"Sesi Fokus #{session}")

        if session < sessions_target:
            print(f"\n{Color.GREEN}{Color.BOLD}☕ WAKTUNYA ISTIRAHAT SINGKAT (5 Menit){Color.RESET}")
            input(f"{Color.YELLOW}Tekan Enter untuk mulai istirahat 5 menit...{Color.RESET}")
            run_countdown(5 * 60, title="Istirahat Singkat")
        else:
            print(f"\n{Color.MAGENTA}{Color.BOLD}🎉 HEBAT! 4 Sesi Pomodoro Selesai!{Color.RESET}")
            print(f"{Color.GREEN}Sekarang saatnya istirahat panjang (15 Menit) 🌟{Color.RESET}")
            choice = input(f"{Color.YELLOW}Mulai istirahat panjang 15 menit? (y/n): {Color.RESET}").strip().lower()
            if choice == 'y':
                run_countdown(15 * 60, title="Istirahat Panjang")

def main():
    while True:
        print_banner()
        print(f"  {Color.WHITE}{Color.BOLD}Silakan Pilih Mode Timer:{Color.RESET}")
        print(f"  {Color.CYAN}1.{Color.RESET} ⏳ Countdown Timer (Hitung Mundur)")
        print(f"  {Color.CYAN}2.{Color.RESET} ⏱️  Stopwatch (dengan Fitur Lap)")
        print(f"  {Color.CYAN}3.{Color.RESET} 🍅 Pomodoro Focus Timer (25m Fokus / 5m Break)")
        print(f"  {Color.CYAN}4.{Color.RESET} ⚡ Preset Cepat (1m, 3m, 5m, 10m)")
        print(f"  {Color.CYAN}5.{Color.RESET} 🚪 Keluar")
        print()

        choice = input(f"  {Color.YELLOW}Pilihan Anda (1-5): {Color.RESET}").strip()

        if choice == '1':
            print(f"\n  {Color.GRAY}Format contoh: '5m', '1h30m', '45s', atau detik langsung '60'{Color.RESET}")
            raw = input(f"  {Color.WHITE}Masukkan durasi waktu: {Color.RESET}").strip()
            sec = parse_time_input(raw)
            if sec > 0:
                run_countdown(sec, title="Hitung Mundur")
            else:
                print(f"  {Color.RED}Input format waktu tidak valid.{Color.RESET}")
                time.sleep(1.5)

        elif choice == '2':
            run_stopwatch()

        elif choice == '3':
            run_pomodoro()

        elif choice == '4':
            print(f"\n  {Color.BOLD}Pilih Preset Cepat:{Color.RESET}")
            print("  a. 1 Menit")
            print("  b. 3 Menit (Rebus Mie/Teh)")
            print("  c. 5 Menit (Quick Break)")
            print("  d. 10 Menit")
            sub = input(f"\n  {Color.YELLOW}Pilih preset (a-d): {Color.RESET}").strip().lower()
            presets = {'a': 60, 'b': 180, 'c': 300, 'd': 600}
            names = {'a': "1 Menit", 'b': "3 Menit", 'c': "5 Menit", 'd': "10 Menit"}
            if sub in presets:
                run_countdown(presets[sub], title=f"Preset {names[sub]}")
            else:
                print(f"  {Color.RED}Preset tidak valid.{Color.RESET}")
                time.sleep(1)

        elif choice == '5':
            print(f"\n  {Color.GREEN}Terima kasih telah menggunakan Python Timer! Sampai jumpa 👋{Color.RESET}\n")
            break
        else:
            print(f"  {Color.RED}Pilihan tidak valid, coba lagi.{Color.RESET}")
            time.sleep(1)

if __name__ == '__main__':
    main()
