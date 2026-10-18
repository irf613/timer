"""
sound_alert.py - Modul notifikasi suara menggunakan winsound bawaan Windows.
Dijalankan di background thread agar tidak memblokir antarmuka (UI).
"""
import threading
import time

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

_sound_enabled = True

def set_sound_enabled(enabled: bool):
    global _sound_enabled
    _sound_enabled = enabled

def is_sound_enabled() -> bool:
    return _sound_enabled

def _beep_thread(notes):
    if not HAS_WINSOUND or not _sound_enabled:
        return
    try:
        for freq, duration_ms in notes:
            if not _sound_enabled:
                break
            winsound.Beep(freq, duration_ms)
            time.sleep(0.03)
    except Exception:
        pass

def play_button_click():
    """Suara klik ringan saat menekan tombol."""
    if not _sound_enabled:
        return
    notes = [(880, 40)]
    threading.Thread(target=_beep_thread, args=(notes,), daemon=True).start()

def play_start_sound():
    """Suara saat timer dimulai."""
    if not _sound_enabled:
        return
    notes = [(523, 80), (659, 100)]
    threading.Thread(target=_beep_thread, args=(notes,), daemon=True).start()

def play_pause_sound():
    """Suara saat timer di-pause."""
    if not _sound_enabled:
        return
    notes = [(659, 80), (523, 100)]
    threading.Thread(target=_beep_thread, args=(notes,), daemon=True).start()

def play_lap_sound():
    """Suara saat mencatat putaran (Lap)."""
    if not _sound_enabled:
        return
    notes = [(784, 60)]
    threading.Thread(target=_beep_thread, args=(notes,), daemon=True).start()

def play_alarm_finished(repeat: int = 3):
    """Suara melodi alarm ketika waktu timer habis."""
    if not _sound_enabled:
        return

    def alarm_worker():
        if not HAS_WINSOUND:
            return
        # Melodi C-E-G-C (akor C mayor ceria) berulang
        melody = [
            (523, 150),  # C5
            (659, 150),  # E5
            (784, 150),  # G5
            (1046, 350), # C6
        ]
        for _ in range(repeat):
            if not _sound_enabled:
                break
            for freq, dur in melody:
                if not _sound_enabled:
                    break
                try:
                    winsound.Beep(freq, dur)
                except Exception:
                    pass
                time.sleep(0.04)
            time.sleep(0.3)

    threading.Thread(target=alarm_worker, daemon=True).start()
