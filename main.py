"""
main.py - Aplikasi Desktop Timer Modern & Lengkap dengan Python (Tkinter)
Fitur:
1. Countdown Timer (dengan gauge lingkaran animasi & preset cepat)
2. Stopwatch Presisi (dengan pencatatan putaran / Lap History)
3. Pomodoro Focus Timer (Focus 25m, Short Break 5m, Long Break 15m)
4. Suara Notifikasi / Alarm Windows
5. Tampilan Elegan Dark Theme High-DPI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import time
import math
import threading
import sound_alert

# Mengaktifkan DPI awareness agar font di Windows terlihat sangat tajam
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

# Palet Warna Tema Cyber-Dark
THEME = {
    "bg": "#0f111a",              # Latar belakang utama
    "card_bg": "#181b29",         # Latar belakang kartu/kontainer
    "card_border": "#282d43",     # Border kartu
    "primary": "#00d2ff",         # Cyan Neon
    "secondary": "#7928ca",       # Ungu Neon
    "accent_green": "#00e676",    # Hijau Sukses/Mulai
    "accent_amber": "#ffab00",    # Kuning/Oranye Jeda
    "accent_red": "#ff3d71",      # Merah Stop/Reset
    "track": "#1e2235",           # Latar belakang arc progress
    "text_main": "#ffffff",       # Teks putih utama
    "text_muted": "#8a99ad",      # Teks abu-abu
    "tab_active": "#242a40",      # Tab aktif
    "tab_inactive": "#131622",    # Tab non-aktif
}

FONT_FAMILY = "Segoe UI"
MONO_FONT = "Consolas"

class ModernButton(tk.Button):
    """Tombol kustom dengan efek hover dan rounded feel"""
    def __init__(self, master, text="", bg_color=THEME["primary"], fg_color="#ffffff", 
                 hover_bg=None, command=None, width=None, height=None, font=(FONT_FAMILY, 10, "bold"), **kwargs):
        self.default_bg = bg_color
        self.hover_bg = hover_bg or self._adjust_brightness(bg_color, 1.2)
        self.default_fg = fg_color

        super().__init__(
            master, text=text, bg=self.default_bg, fg=self.default_fg,
            activebackground=self.hover_bg, activeforeground=self.default_fg,
            relief="flat", bd=0, font=font, cursor="hand2",
            command=command, padx=14, pady=8, **kwargs
        )
        if width:
            self.configure(width=width)
        if height:
            self.configure(height=height)

        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self.configure(bg=self.hover_bg)

    def on_leave(self, e):
        self.configure(bg=self.default_bg)

    def update_colors(self, bg_color, hover_bg=None, fg_color="#ffffff"):
        self.default_bg = bg_color
        self.hover_bg = hover_bg or self._adjust_brightness(bg_color, 1.2)
        self.default_fg = fg_color
        self.configure(bg=self.default_bg, fg=self.default_fg)

    def _adjust_brightness(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return hex_color
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        return f"#{r:02x}{g:02x}{b:02x}"

class TimerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python Timer Pro ⏱️")
        self.geometry("560x740")
        self.minsize(520, 680)
        self.configure(bg=THEME["bg"])

        # State Umum
        self.current_tab = "timer"
        self.sound_enabled = tk.BooleanVar(value=True)

        # State Countdown Timer
        self.timer_running = False
        self.timer_paused = False
        self.timer_total_seconds = 300 # Default 5 menit
        self.timer_remaining_seconds = 300
        self.timer_after_id = None
        self.timer_flash_state = False

        # State Stopwatch
        self.sw_running = False
        self.sw_start_time = 0.0
        self.sw_elapsed = 0.0
        self.sw_after_id = None
        self.sw_laps = []
        self.sw_last_lap_time = 0.0

        # State Pomodoro
        self.pomo_running = False
        self.pomo_paused = False
        self.pomo_mode = "focus" # 'focus', 'short_break', 'long_break'
        self.pomo_durations = {"focus": 25 * 60, "short_break": 5 * 60, "long_break": 15 * 60}
        self.pomo_remaining = self.pomo_durations["focus"]
        self.pomo_total = self.pomo_durations["focus"]
        self.pomo_cycle = 1
        self.pomo_after_id = None

        self._setup_ui()

    def _setup_ui(self):
        # 1. Top Header Bar
        self.header_frame = tk.Frame(self, bg=THEME["bg"])
        self.header_frame.pack(fill="x", padx=24, pady=(16, 10))

        title_lbl = tk.Label(
            self.header_frame, text="⚡ TIMER PRO", 
            font=(FONT_FAMILY, 15, "bold"), bg=THEME["bg"], fg=THEME["primary"]
        )
        title_lbl.pack(side="left")

        # Sound Toggle Button
        self.btn_sound = tk.Button(
            self.header_frame, text="🔊 Suara: ON", font=(FONT_FAMILY, 9, "bold"),
            bg=THEME["card_bg"], fg=THEME["text_muted"], relief="flat", bd=0,
            padx=10, pady=4, cursor="hand2", command=self._toggle_sound
        )
        self.btn_sound.pack(side="right")

        # 2. Modern Tab Navigation Bar
        self.tab_bar = tk.Frame(self, bg=THEME["card_bg"], highlightbackground=THEME["card_border"], highlightthickness=1)
        self.tab_bar.pack(fill="x", padx=24, pady=10)

        self.tab_buttons = {}
        tabs = [
            ("timer", "⏳ Countdown"),
            ("stopwatch", "⏱️ Stopwatch"),
            ("pomodoro", "🍅 Pomodoro")
        ]

        for tab_id, label in tabs:
            btn = tk.Button(
                self.tab_bar, text=label, font=(FONT_FAMILY, 10, "bold"),
                relief="flat", bd=0, padx=16, pady=10, cursor="hand2",
                command=lambda tid=tab_id: self._switch_tab(tid)
            )
            btn.pack(side="left", expand=True, fill="x")
            self.tab_buttons[tab_id] = btn

        # 3. Main Container for views
        self.container = tk.Frame(self, bg=THEME["bg"])
        self.container.pack(fill="both", expand=True, padx=24, pady=(10, 20))

        # Build subframes
        self.frame_timer = tk.Frame(self.container, bg=THEME["bg"])
        self.frame_stopwatch = tk.Frame(self.container, bg=THEME["bg"])
        self.frame_pomodoro = tk.Frame(self.container, bg=THEME["bg"])

        self._build_timer_view()
        self._build_stopwatch_view()
        self._build_pomodoro_view()

        # Set default tab
        self._switch_tab("timer")

    def _toggle_sound(self):
        new_state = not self.sound_enabled.get()
        self.sound_enabled.set(new_state)
        sound_alert.set_sound_enabled(new_state)
        if new_state:
            self.btn_sound.configure(text="🔊 Suara: ON", fg=THEME["accent_green"])
            sound_alert.play_button_click()
        else:
            self.btn_sound.configure(text="🔇 Suara: OFF", fg=THEME["text_muted"])

    def _switch_tab(self, tab_id):
        self.current_tab = tab_id
        for tid, btn in self.tab_buttons.items():
            if tid == tab_id:
                btn.configure(bg=THEME["tab_active"], fg=THEME["primary"])
            else:
                btn.configure(bg=THEME["tab_inactive"], fg=THEME["text_muted"])

        # Hide all frames and show selected
        self.frame_timer.pack_forget()
        self.frame_stopwatch.pack_forget()
        self.frame_pomodoro.pack_forget()

        if tab_id == "timer":
            self.frame_timer.pack(fill="both", expand=True)
        elif tab_id == "stopwatch":
            self.frame_stopwatch.pack(fill="both", expand=True)
        elif tab_id == "pomodoro":
            self.frame_pomodoro.pack(fill="both", expand=True)

    # ==========================================
    # 1. COUNTDOWN TIMER VIEW
    # ==========================================
    def _build_timer_view(self):
        # Card Wrapper
        card = tk.Frame(self.frame_timer, bg=THEME["card_bg"], highlightbackground=THEME["card_border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Circular Gauge Canvas
        self.timer_canvas_size = 240
        self.timer_canvas = tk.Canvas(
            card, width=self.timer_canvas_size, height=self.timer_canvas_size,
            bg=THEME["card_bg"], highlightthickness=0
        )
        self.timer_canvas.pack(pady=(16, 8))

        # Quick Presets Buttons Frame
        presets_frame = tk.Frame(card, bg=THEME["card_bg"])
        presets_frame.pack(fill="x", padx=20, pady=(4, 12))

        lbl_preset = tk.Label(presets_frame, text="Preset Cepat:", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"])
        lbl_preset.pack(anchor="w", pady=(0, 4))

        p_btn_row = tk.Frame(presets_frame, bg=THEME["card_bg"])
        p_btn_row.pack(fill="x")

        presets = [("+1m", 60), ("+3m", 180), ("+5m", 300), ("+10m", 600), ("+15m", 900), ("+30m", 1800)]
        for label, sec in presets:
            b = tk.Button(
                p_btn_row, text=label, font=(FONT_FAMILY, 9, "bold"),
                bg=THEME["tab_active"], fg=THEME["text_main"], relief="flat", bd=0,
                padx=8, pady=4, cursor="hand2", command=lambda s=sec: self._add_timer_time(s)
            )
            b.pack(side="left", expand=True, fill="x", padx=2)

        # Manual Custom Input Row (Jam : Menit : Detik)
        input_box = tk.Frame(card, bg=THEME["card_bg"])
        input_box.pack(pady=4)

        input_title = tk.Label(input_box, text="Atur Manual (J : M : D):", font=(FONT_FAMILY, 9), bg=THEME["card_bg"], fg=THEME["text_muted"])
        input_title.pack()

        spin_frame = tk.Frame(input_box, bg=THEME["card_bg"])
        spin_frame.pack(pady=4)

        self.spin_h = ttk.Spinbox(spin_frame, from_=0, to=23, width=3, font=(MONO_FONT, 12, "bold"), justify="center")
        self.spin_m = ttk.Spinbox(spin_frame, from_=0, to=59, width=3, font=(MONO_FONT, 12, "bold"), justify="center")
        self.spin_s = ttk.Spinbox(spin_frame, from_=0, to=59, width=3, font=(MONO_FONT, 12, "bold"), justify="center")
        self.spin_h.set("0")
        self.spin_m.set("5")
        self.spin_s.set("0")

        self.spin_h.pack(side="left", padx=2)
        tk.Label(spin_frame, text=":", font=(MONO_FONT, 12, "bold"), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(side="left")
        self.spin_m.pack(side="left", padx=2)
        tk.Label(spin_frame, text=":", font=(MONO_FONT, 12, "bold"), bg=THEME["card_bg"], fg=THEME["text_muted"]).pack(side="left")
        self.spin_s.pack(side="left", padx=2)

        btn_set_custom = tk.Button(
            spin_frame, text="Set", font=(FONT_FAMILY, 8, "bold"),
            bg=THEME["tab_active"], fg=THEME["primary"], relief="flat", bd=0,
            padx=8, pady=2, cursor="hand2", command=self._apply_custom_timer
        )
        btn_set_custom.pack(side="left", padx=6)

        # Action Buttons (Start/Pause, Reset)
        btn_action_frame = tk.Frame(card, bg=THEME["card_bg"])
        btn_action_frame.pack(pady=(16, 20))

        self.btn_timer_start = ModernButton(
            btn_action_frame, text="▶ MULAI", bg_color=THEME["accent_green"],
            width=12, command=self._toggle_timer_start
        )
        self.btn_timer_start.pack(side="left", padx=8)

        self.btn_timer_reset = ModernButton(
            btn_action_frame, text="↺ RESET", bg_color=THEME["tab_active"],
            fg_color=THEME["text_muted"], width=10, command=self._reset_timer
        )
        self.btn_timer_reset.pack(side="left", padx=8)

        # Inisialisasi tampilan canvas
        self._redraw_timer_canvas()

    def _draw_circular_progress(self, canvas, size, percent, text_center, subtext="", color=THEME["primary"]):
        canvas.delete("all")
        margin = 18
        stroke_w = 12
        x0, y0 = margin, margin
        x1, y1 = size - margin, size - margin

        # Background track
        canvas.create_arc(
            x0, y0, x1, y1, start=90, extent=-360,
            style="arc", width=stroke_w, outline=THEME["track"]
        )

        # Progress Arc
        extent_angle = -360.0 * percent
        if abs(extent_angle) > 0.1:
            canvas.create_arc(
                x0, y0, x1, y1, start=90, extent=extent_angle,
                style="arc", width=stroke_w, outline=color
            )

        # Center Texts
        center_x = size / 2
        center_y = size / 2

        canvas.create_text(
            center_x, center_y - 6,
            text=text_center, font=(MONO_FONT, 28, "bold"), fill=THEME["text_main"]
        )
        if subtext:
            canvas.create_text(
                center_x, center_y + 26,
                text=subtext, font=(FONT_FAMILY, 9), fill=THEME["text_muted"]
            )

    def _format_time_str(self, total_seconds):
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def _redraw_timer_canvas(self):
        fraction = 0.0
        if self.timer_total_seconds > 0:
            fraction = self.timer_remaining_seconds / self.timer_total_seconds

        time_str = self._format_time_str(self.timer_remaining_seconds)

        if self.timer_remaining_seconds == 0:
            status = "SELESAI!"
            color = THEME["accent_red"]
        elif self.timer_paused:
            status = "DIJEDA"
            color = THEME["accent_amber"]
        elif self.timer_running:
            status = "BERJALAN"
            color = THEME["primary"]
        else:
            status = "SIAP"
            color = THEME["primary"]

        self._draw_circular_progress(
            self.timer_canvas, self.timer_canvas_size, fraction,
            time_str, subtext=status, color=color
        )

    def _add_timer_time(self, seconds):
        if not self.timer_running:
            self.timer_total_seconds += seconds
            self.timer_remaining_seconds += seconds
        else:
            self.timer_total_seconds += seconds
            self.timer_remaining_seconds += seconds
        self._redraw_timer_canvas()
        sound_alert.play_button_click()

    def _apply_custom_timer(self):
        try:
            h = int(self.spin_h.get())
            m = int(self.spin_m.get())
            s = int(self.spin_s.get())
            total = h * 3600 + m * 60 + s
            if total <= 0:
                messagebox.showwarning("Waktu Tidak Valid", "Masukkan waktu lebih dari 0 detik!")
                return
            self._reset_timer()
            self.timer_total_seconds = total
            self.timer_remaining_seconds = total
            self._redraw_timer_canvas()
            sound_alert.play_button_click()
        except ValueError:
            messagebox.showerror("Error", "Masukkan format angka yang benar!")

    def _toggle_timer_start(self):
        if not self.timer_running:
            if self.timer_remaining_seconds <= 0:
                self.timer_remaining_seconds = self.timer_total_seconds
            self.timer_running = True
            self.timer_paused = False
            self.btn_timer_start.configure(text="⏸ JEDA")
            self.btn_timer_start.update_colors(THEME["accent_amber"])
            sound_alert.play_start_sound()
            self._timer_tick()
        elif self.timer_running and not self.timer_paused:
            # Pause
            self.timer_paused = True
            self.timer_running = False
            if self.timer_after_id:
                self.after_cancel(self.timer_after_id)
            self.btn_timer_start.configure(text="▶ LANJUT")
            self.btn_timer_start.update_colors(THEME["accent_green"])
            sound_alert.play_pause_sound()
            self._redraw_timer_canvas()

    def _timer_tick(self):
        if self.timer_running and self.timer_remaining_seconds > 0:
            self.timer_remaining_seconds -= 1
            self._redraw_timer_canvas()
            if self.timer_remaining_seconds == 0:
                self._timer_finished()
            else:
                self.timer_after_id = self.after(1000, self._timer_tick)

    def _timer_finished(self):
        self.timer_running = False
        self.timer_paused = False
        self.btn_timer_start.configure(text="▶ MULAI")
        self.btn_timer_start.update_colors(THEME["accent_green"])
        self._redraw_timer_canvas()
        sound_alert.play_alarm_finished(repeat=3)

    def _reset_timer(self):
        if self.timer_after_id:
            self.after_cancel(self.timer_after_id)
        self.timer_running = False
        self.timer_paused = False
        self.timer_remaining_seconds = self.timer_total_seconds
        self.btn_timer_start.configure(text="▶ MULAI")
        self.btn_timer_start.update_colors(THEME["accent_green"])
        self._redraw_timer_canvas()
        sound_alert.play_button_click()

    # ==========================================
    # 2. STOPWATCH VIEW
    # ==========================================
    def _build_stopwatch_view(self):
        card = tk.Frame(self.frame_stopwatch, bg=THEME["card_bg"], highlightbackground=THEME["card_border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Big Digital Stopwatch Display
        display_frame = tk.Frame(card, bg=THEME["track"], padx=20, pady=24)
        display_frame.pack(fill="x", padx=20, pady=(20, 10))

        self.lbl_sw_time = tk.Label(
            display_frame, text="00:00:00.00", font=(MONO_FONT, 34, "bold"),
            bg=THEME["track"], fg=THEME["primary"]
        )
        self.lbl_sw_time.pack()

        self.lbl_sw_sub = tk.Label(
            display_frame, text="STOPWATCH SIAP", font=(FONT_FAMILY, 9),
            bg=THEME["track"], fg=THEME["text_muted"]
        )
        self.lbl_sw_sub.pack(pady=(4, 0))

        # Action Buttons (Start, Lap, Reset)
        sw_btn_frame = tk.Frame(card, bg=THEME["card_bg"])
        sw_btn_frame.pack(pady=12)

        self.btn_sw_start = ModernButton(
            sw_btn_frame, text="▶ START", bg_color=THEME["accent_green"],
            width=10, command=self._toggle_stopwatch
        )
        self.btn_sw_start.pack(side="left", padx=6)

        self.btn_sw_lap = ModernButton(
            sw_btn_frame, text="🚩 LAP", bg_color=THEME["tab_active"],
            fg_color=THEME["text_main"], width=8, command=self._record_lap
        )
        self.btn_sw_lap.pack(side="left", padx=6)

        self.btn_sw_reset = ModernButton(
            sw_btn_frame, text="↺ RESET", bg_color=THEME["tab_active"],
            fg_color=THEME["text_muted"], width=8, command=self._reset_stopwatch
        )
        self.btn_sw_reset.pack(side="left", padx=6)

        # Lap Times History Table
        lbl_history = tk.Label(card, text="Riwayat Putaran (Lap History):", font=(FONT_FAMILY, 9, "bold"), bg=THEME["card_bg"], fg=THEME["text_muted"])
        lbl_history.pack(anchor="w", padx=24, pady=(8, 4))

        table_frame = tk.Frame(card, bg=THEME["card_bg"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 16))

        # Treeview styling
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Lap.Treeview",
            background=THEME["bg"],
            foreground=THEME["text_main"],
            fieldbackground=THEME["bg"],
            rowheight=26,
            font=(FONT_FAMILY, 9)
        )
        style.configure("Lap.Treeview.Heading", background=THEME["tab_active"], foreground=THEME["primary"], font=(FONT_FAMILY, 9, "bold"))
        style.map("Lap.Treeview", background=[("selected", THEME["tab_active"])])

        self.sw_tree = ttk.Treeview(table_frame, columns=("lap", "lap_time", "total_time"), show="headings", style="Lap.Treeview", height=7)
        self.sw_tree.heading("lap", text="Lap #")
        self.sw_tree.heading("lap_time", text="Durasi Lap")
        self.sw_tree.heading("total_time", text="Total Waktu")
        self.sw_tree.column("lap", width=60, anchor="center")
        self.sw_tree.column("lap_time", width=140, anchor="center")
        self.sw_tree.column("total_time", width=140, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.sw_tree.yview)
        self.sw_tree.configure(yscrollcommand=scrollbar.set)

        self.sw_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _toggle_stopwatch(self):
        if not self.sw_running:
            # Start
            self.sw_running = True
            self.sw_start_time = time.time() - self.sw_elapsed
            self.btn_sw_start.configure(text="⏸ PAUSE")
            self.btn_sw_start.update_colors(THEME["accent_amber"])
            self.lbl_sw_sub.configure(text="BERJALAN...", fg=THEME["accent_green"])
            sound_alert.play_start_sound()
            self._stopwatch_tick()
        else:
            # Pause
            self.sw_running = False
            if self.sw_after_id:
                self.after_cancel(self.sw_after_id)
            self.btn_sw_start.configure(text="▶ RESUME")
            self.btn_sw_start.update_colors(THEME["accent_green"])
            self.lbl_sw_sub.configure(text="DIJEDA", fg=THEME["accent_amber"])
            sound_alert.play_pause_sound()

    def _stopwatch_tick(self):
        if self.sw_running:
            self.sw_elapsed = time.time() - self.sw_start_time
            m = int(self.sw_elapsed // 60)
            s = int(self.sw_elapsed % 60)
            ms = int((self.sw_elapsed * 100) % 100)
            h = int(self.sw_elapsed // 3600)
            self.lbl_sw_time.configure(text=f"{h:02d}:{m:02d}:{s:02d}.{ms:02d}")
            self.sw_after_id = self.after(30, self._stopwatch_tick)

    def _record_lap(self):
        if not self.sw_running and self.sw_elapsed == 0.0:
            return
        current_time = self.sw_elapsed
        lap_duration = current_time - self.sw_last_lap_time
        self.sw_last_lap_time = current_time

        lap_idx = len(self.sw_laps) + 1
        self.sw_laps.append((lap_duration, current_time))

        def fmt(t):
            m = int(t // 60)
            s = int(t % 60)
            ms = int((t * 100) % 100)
            return f"{m:02d}:{s:02d}.{ms:02d}"

        # Insert at top of list
        self.sw_tree.insert("", 0, values=(f"#{lap_idx:02d}", f"+{fmt(lap_duration)}", fmt(current_time)))
        sound_alert.play_lap_sound()

    def _reset_stopwatch(self):
        if self.sw_after_id:
            self.after_cancel(self.sw_after_id)
        self.sw_running = False
        self.sw_elapsed = 0.0
        self.sw_last_lap_time = 0.0
        self.sw_laps.clear()
        self.lbl_sw_time.configure(text="00:00:00.00")
        self.lbl_sw_sub.configure(text="STOPWATCH SIAP", fg=THEME["text_muted"])
        self.btn_sw_start.configure(text="▶ START")
        self.btn_sw_start.update_colors(THEME["accent_green"])
        for row in self.sw_tree.get_children():
            self.sw_tree.delete(row)
        sound_alert.play_button_click()

    # ==========================================
    # 3. POMODORO VIEW
    # ==========================================
    def _build_pomodoro_view(self):
        card = tk.Frame(self.frame_pomodoro, bg=THEME["card_bg"], highlightbackground=THEME["card_border"], highlightthickness=1)
        card.pack(fill="both", expand=True, padx=4, pady=4)

        # Mode Selector Buttons (Focus, Short Break, Long Break)
        pomo_selector = tk.Frame(card, bg=THEME["card_bg"])
        pomo_selector.pack(fill="x", padx=20, pady=(16, 6))

        self.pomo_mode_btns = {}
        modes = [
            ("focus", "🎯 Fokus (25m)"),
            ("short_break", "☕ Rehat (5m)"),
            ("long_break", "🌴 Istirahat (15m)")
        ]
        for mid, label in modes:
            btn = tk.Button(
                pomo_selector, text=label, font=(FONT_FAMILY, 9, "bold"),
                relief="flat", bd=0, padx=10, pady=6, cursor="hand2",
                command=lambda m=mid: self._set_pomodoro_mode(m)
            )
            btn.pack(side="left", expand=True, fill="x", padx=3)
            self.pomo_mode_btns[mid] = btn

        # Pomodoro Circular Gauge
        self.pomo_canvas_size = 230
        self.pomo_canvas = tk.Canvas(
            card, width=self.pomo_canvas_size, height=self.pomo_canvas_size,
            bg=THEME["card_bg"], highlightthickness=0
        )
        self.pomo_canvas.pack(pady=(10, 8))

        # Cycle Counter Indicator
        self.lbl_pomo_cycle = tk.Label(
            card, text="Siklus Sesi: ● ○ ○ ○ (1 / 4)",
            font=(FONT_FAMILY, 10, "bold"), bg=THEME["card_bg"], fg=THEME["primary"]
        )
        self.lbl_pomo_cycle.pack(pady=4)

        # Control Buttons
        pomo_actions = tk.Frame(card, bg=THEME["card_bg"])
        pomo_actions.pack(pady=(12, 20))

        self.btn_pomo_start = ModernButton(
            pomo_actions, text="▶ MULAI FOKUS", bg_color=THEME["accent_green"],
            width=14, command=self._toggle_pomodoro
        )
        self.btn_pomo_start.pack(side="left", padx=8)

        self.btn_pomo_skip = ModernButton(
            pomo_actions, text="⏭ LEWATI", bg_color=THEME["tab_active"],
            fg_color=THEME["text_muted"], width=10, command=self._skip_pomodoro
        )
        self.btn_pomo_skip.pack(side="left", padx=8)

        self._update_pomo_mode_buttons()
        self._redraw_pomodoro_canvas()

    def _set_pomodoro_mode(self, mode):
        if self.pomo_after_id:
            self.after_cancel(self.pomo_after_id)
        self.pomo_mode = mode
        self.pomo_running = False
        self.pomo_paused = False
        self.pomo_total = self.pomo_durations[mode]
        self.pomo_remaining = self.pomo_total
        self.btn_pomo_start.configure(text="▶ MULAI")
        self.btn_pomo_start.update_colors(THEME["accent_green"])
        self._update_pomo_mode_buttons()
        self._redraw_pomodoro_canvas()
        sound_alert.play_button_click()

    def _update_pomo_mode_buttons(self):
        for mid, btn in self.pomo_mode_btns.items():
            if mid == self.pomo_mode:
                btn.configure(bg=THEME["primary"], fg="#000000")
            else:
                btn.configure(bg=THEME["tab_active"], fg=THEME["text_muted"])

    def _redraw_pomodoro_canvas(self):
        fraction = 0.0
        if self.pomo_total > 0:
            fraction = self.pomo_remaining / self.pomo_total

        time_str = self._format_time_str(self.pomo_remaining)

        mode_titles = {
            "focus": ("FOKUS KERJA", THEME["accent_green"]),
            "short_break": ("ISTIRAHAT SINGKAT", THEME["accent_amber"]),
            "long_break": ("ISTIRAHAT PANJANG", THEME["secondary"])
        }
        title, color = mode_titles[self.pomo_mode]

        self._draw_circular_progress(
            self.pomo_canvas, self.pomo_canvas_size, fraction,
            time_str, subtext=title, color=color
        )

    def _toggle_pomodoro(self):
        if not self.pomo_running:
            self.pomo_running = True
            self.pomo_paused = False
            self.btn_pomo_start.configure(text="⏸ JEDA")
            self.btn_pomo_start.update_colors(THEME["accent_amber"])
            sound_alert.play_start_sound()
            self._pomo_tick()
        else:
            self.pomo_running = False
            self.pomo_paused = True
            if self.pomo_after_id:
                self.after_cancel(self.pomo_after_id)
            self.btn_pomo_start.configure(text="▶ LANJUT")
            self.btn_pomo_start.update_colors(THEME["accent_green"])
            sound_alert.play_pause_sound()
            self._redraw_pomodoro_canvas()

    def _pomo_tick(self):
        if self.pomo_running and self.pomo_remaining > 0:
            self.pomo_remaining -= 1
            self._redraw_pomodoro_canvas()
            if self.pomo_remaining == 0:
                self._pomo_finished()
            else:
                self.pomo_after_id = self.after(1000, self._pomo_tick)

    def _pomo_finished(self):
        self.pomo_running = False
        sound_alert.play_alarm_finished(repeat=3)

        if self.pomo_mode == "focus":
            if self.pomo_cycle < 4:
                messagebox.showinfo("Pomodoro Selesai!", f"Sesi Fokus #{self.pomo_cycle} Selesai! Saatnya istirahat 5 menit ☕")
                self.pomo_cycle += 1
                self._set_pomodoro_mode("short_break")
            else:
                messagebox.showinfo("Pomodoro Selesai!", "Hebat! 4 Sesi Fokus selesai! Nikmati istirahat panjang 15 menit 🌴")
                self.pomo_cycle = 1
                self._set_pomodoro_mode("long_break")
        else:
            messagebox.showinfo("Istirahat Selesai!", "Waktu istirahat selesai! Mari kembali fokus 💪")
            self._set_pomodoro_mode("focus")

        self._update_pomo_cycle_indicator()

    def _skip_pomodoro(self):
        if self.pomo_mode == "focus":
            self._set_pomodoro_mode("short_break")
        else:
            self._set_pomodoro_mode("focus")
        sound_alert.play_button_click()

    def _update_pomo_cycle_indicator(self):
        dots = ""
        for i in range(1, 5):
            dots += "● " if i <= self.pomo_cycle else "○ "
        self.lbl_pomo_cycle.configure(text=f"Siklus Sesi: {dots.strip()} ({self.pomo_cycle} / 4)")

def main():
    app = TimerApp()
    app.mainloop()

if __name__ == "__main__":
    main()
