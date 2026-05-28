import tkinter as tk
import math
import platform

# ── Sound support (Windows winsound, fallback silent) ──────────────────────
try:
    import winsound
    def _beep(freq, duration):
        winsound.Beep(freq, duration)
except ImportError:
    def _beep(freq, duration):
        pass

# ── Colour palette ──────────────────────────────────────────────────────────
BG          = "#0a0a0f"
PANEL       = "#0f0f1a"
ACCENT_WORK = "#00f5ff"      # cyan  – focus
ACCENT_SB   = "#a259ff"      # violet – short break
ACCENT_LB   = "#00ff88"      # green  – long break
TRACK_CLR   = "#1a1a2e"
TEXT_DIM    = "#3a3a5c"
TEXT_BRIGHT = "#e0e0ff"
BTN_HOVER   = "#1a1a2e"

# ── Default durations (seconds) ─────────────────────────────────────────────
DEFAULT_WORK  = 30 * 60
DEFAULT_SB    =  7 * 60
DEFAULT_LB    = 20 * 60
POMODOROS_BEFORE_LB = 4

# ── Canvas geometry ─────────────────────────────────────────────────────────
WIN_W, WIN_H   = 480, 640
CX, CY         = WIN_W // 2, 240
RADIUS         = 160
ARC_WIDTH      = 14
BTN_Y_START    = 430

# ═══════════════════════════════════════════════════════════════════════════
class PomodoroTimer:
    # ── init ────────────────────────────────────────────────────────────────
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("POMODORO  ◈  FOCUS TIMER")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        # ── State ────────────────────────────────────────────────────────
        self.work_time   = DEFAULT_WORK
        self.short_break = DEFAULT_SB
        self.long_break  = DEFAULT_LB

        self.mode        = "work"   # "work" | "short" | "long"
        self.is_running  = False
        self.after_id    = None
        self.pomodoros   = 0
        self.time_left   = self.work_time
        self.total_time  = self.work_time

        # ── Build UI ─────────────────────────────────────────────────────
        self._build_canvas()
        self._build_settings_panel()
        self._build_buttons()
        self._build_stats()

        self._update_display()
        self.root.mainloop()

    # ── Canvas (arc clock) ──────────────────────────────────────────────────
    def _build_canvas(self):
        self.canvas = tk.Canvas(
            self.root, width=WIN_W, height=410,
            bg=BG, highlightthickness=0
        )
        self.canvas.pack()

        # Decorative ring dots
        for i in range(60):
            angle = math.radians(i * 6 - 90)
            r = RADIUS + ARC_WIDTH + 12
            x = CX + r * math.cos(angle)
            y = CY + r * math.sin(angle)
            size = 3 if i % 5 == 0 else 1
            clr  = TEXT_DIM if i % 5 == 0 else "#1a1a2e"
            self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=clr, outline="")

        # Track circle
        self.canvas.create_oval(
            CX - RADIUS, CY - RADIUS,
            CX + RADIUS, CY + RADIUS,
            outline=TRACK_CLR, width=ARC_WIDTH
        )

        # Progress arc (start item so we can update it)
        self.arc = self.canvas.create_arc(
            CX - RADIUS, CY - RADIUS,
            CX + RADIUS, CY + RADIUS,
            start=90, extent=0,
            outline=ACCENT_WORK, width=ARC_WIDTH,
            style=tk.ARC
        )

        # Glow dot at arc tip (redrawn dynamically)
        self.glow_dot = self.canvas.create_oval(
            CX - 6, CY - RADIUS - 6,
            CX + 6, CY - RADIUS + 6,
            fill=ACCENT_WORK, outline=""
        )

        # Mode label  (e.g. "FOCUS SESSION")
        self.mode_label = self.canvas.create_text(
            CX, CY - 55,
            text="FOCUS SESSION",
            font=("Courier", 11, "bold"),
            fill=ACCENT_WORK, anchor="center"
        )

        # Timer text  MM:SS
        self.time_text = self.canvas.create_text(
            CX, CY + 10,
            text="25:00",
            font=("Courier", 52, "bold"),
            fill=TEXT_BRIGHT, anchor="center"
        )

        # Sub-label  "session X of Y"
        self.sub_label = self.canvas.create_text(
            CX, CY + 65,
            text=f"session 1  of  {POMODOROS_BEFORE_LB}",
            font=("Courier", 11),
            fill=TEXT_DIM, anchor="center"
        )

        # Pomodoro count dots
        self.dot_ids = []
        dot_spacing = 22
        dot_total   = POMODOROS_BEFORE_LB
        start_x     = CX - (dot_total - 1) * dot_spacing / 2
        for i in range(dot_total):
            x = start_x + i * dot_spacing
            y = CY + 98
            did = self.canvas.create_oval(
                x - 6, y - 6, x + 6, y + 6,
                fill=TRACK_CLR, outline=TEXT_DIM, width=1
            )
            self.dot_ids.append(did)

    # ── Settings panel  ─────────────────────────────────────────────────────
    def _build_settings_panel(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=(0, 4))

        labels  = ["FOCUS", "S.BREAK", "L.BREAK"]
        attrs   = ["work_time", "short_break", "long_break"]
        clrs    = [ACCENT_WORK, ACCENT_SB, ACCENT_LB]
        defaults= [25, 5, 15]
        self._vars = []

        for col, (lbl, attr, clr, dflt) in enumerate(zip(labels, attrs, clrs, defaults)):
            col_f = tk.Frame(frame, bg=BG)
            col_f.grid(row=0, column=col, padx=12)

            tk.Label(col_f, text=lbl, font=("Courier", 8, "bold"),
                     fg=clr, bg=BG).pack()

            var = tk.IntVar(value=dflt)
            self._vars.append((attr, var))

            spin = tk.Spinbox(
                col_f, from_=1, to=90, textvariable=var,
                width=4, font=("Courier", 13, "bold"),
                fg=clr, bg=PANEL, insertbackground=clr,
                relief="flat", justify="center",
                buttonbackground=PANEL, disabledforeground=TEXT_DIM,
                command=lambda a=attr, v=var: self._on_setting_change(a, v)
            )
            spin.pack()
            tk.Label(col_f, text="min", font=("Courier", 8),
                     fg=TEXT_DIM, bg=BG).pack()

    def _on_setting_change(self, attr: str, var: tk.IntVar):
        minutes = max(1, var.get())
        setattr(self, attr, minutes * 60)
        if not self.is_running:
            self.time_left  = self.work_time
            self.total_time = self.work_time
            self._update_display()

    # ── Pill-style buttons ──────────────────────────────────────────────────
    def _make_button(self, parent, text, command, accent, row, col):
        btn = tk.Label(
            parent, text=text,
            font=("Courier", 11, "bold"),
            fg=accent, bg=PANEL,
            width=10, pady=9,
            relief="flat", cursor="hand2"
        )
        btn.grid(row=row, column=col, padx=8, pady=4)
        btn.bind("<Button-1>",        lambda e: command())
        btn.bind("<Enter>",           lambda e, b=btn, a=accent: b.config(bg=a, fg=BG))
        btn.bind("<Leave>",           lambda e, b=btn, a=accent: b.config(bg=PANEL, fg=a))
        return btn

    def _build_buttons(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=8)

        self.start_btn = self._make_button(frame, "▶  START",  self.start_timer, ACCENT_WORK, 0, 0)
        self.pause_btn = self._make_button(frame, "⏸  PAUSE",  self.pause_timer, ACCENT_SB,   0, 1)
        self.reset_btn = self._make_button(frame, "↺  RESET",  self.reset_timer, ACCENT_LB,   0, 2)

        self.pause_btn.config(state="disabled", fg=TEXT_DIM)
        self.pause_btn.unbind("<Enter>")
        self.pause_btn.unbind("<Leave>")

    # ── Stats footer ────────────────────────────────────────────────────────
    def _build_stats(self):
        frame = tk.Frame(self.root, bg=BG)
        frame.pack(pady=(2, 0))

        tk.Label(frame, text="TODAY'S SESSIONS", font=("Courier", 8),
                 fg=TEXT_DIM, bg=BG).pack()

        self.total_label = tk.Label(
            frame, text="0  pomodoros  completed",
            font=("Courier", 11, "bold"),
            fg=TEXT_BRIGHT, bg=BG
        )
        self.total_label.pack()

    # ── Timer logic ─────────────────────────────────────────────────────────
    def start_timer(self):
        if self.is_running:
            return
        self.is_running = True
        self._set_btn_state(self.start_btn, disabled=True,  accent=ACCENT_WORK)
        self._set_btn_state(self.pause_btn, disabled=False, accent=ACCENT_SB)
        self._tick()

    def pause_timer(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self._set_btn_state(self.start_btn, disabled=False, accent=ACCENT_WORK)
        self._set_btn_state(self.pause_btn, disabled=True,  accent=ACCENT_SB)

    def reset_timer(self):
        self.is_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
        self.mode       = "work"
        self.time_left  = self.work_time
        self.total_time = self.work_time
        self._set_btn_state(self.start_btn, disabled=False, accent=ACCENT_WORK)
        self._set_btn_state(self.pause_btn, disabled=True,  accent=ACCENT_SB)
        self._update_display()

    def _tick(self):
        if not self.is_running:
            return
        if self.time_left > 0:
            self.time_left -= 1
            self._update_display()
            self.after_id = self.root.after(1000, self._tick)
        else:
            self._session_complete()

    def _session_complete(self):
        self.is_running = False
        accent = self._accent()

        if self.mode == "work":
            self.pomodoros += 1
            self._play_work_end()
            if self.pomodoros % POMODOROS_BEFORE_LB == 0:
                self.mode       = "long"
                self.time_left  = self.long_break
                self.total_time = self.long_break
            else:
                self.mode       = "short"
                self.time_left  = self.short_break
                self.total_time = self.short_break
        else:
            self._play_break_end()
            self.mode       = "work"
            self.time_left  = self.work_time
            self.total_time = self.work_time

        self._set_btn_state(self.start_btn, disabled=False, accent=ACCENT_WORK)
        self._set_btn_state(self.pause_btn, disabled=True,  accent=ACCENT_SB)
        self._flash_canvas(3)
        self._update_display()

    # ── Display update ───────────────────────────────────────────────────────
    def _update_display(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.canvas.itemconfig(self.time_text, text=f"{mins:02d}:{secs:02d}")

        # Arc
        ratio   = self.time_left / max(self.total_time, 1)
        extent  = -360 * ratio          # negative = clockwise
        accent  = self._accent()
        self.canvas.itemconfig(self.arc, extent=extent, outline=accent)

        # Glow dot position
        angle = math.radians(90 + 360 * ratio)  # 90 = top (12 o'clock)
        gx = CX + RADIUS * math.cos(angle)
        gy = CY - RADIUS * math.sin(angle)
        r  = 7
        self.canvas.coords(self.glow_dot, gx-r, gy-r, gx+r, gy+r)
        self.canvas.itemconfig(self.glow_dot, fill=accent)

        # Mode label & colors
        mode_text = {
            "work":  "◉  FOCUS SESSION",
            "short": "◎  SHORT BREAK",
            "long":  "◎  LONG BREAK",
        }[self.mode]
        self.canvas.itemconfig(self.mode_label, text=mode_text, fill=accent)

        # Session sub-label
        cycle_pos = (self.pomodoros % POMODOROS_BEFORE_LB) + (1 if self.mode == "work" else 0)
        self.canvas.itemconfig(
            self.sub_label,
            text=f"session {cycle_pos}  of  {POMODOROS_BEFORE_LB}"
        )

        # Dot colours
        done_in_cycle = self.pomodoros % POMODOROS_BEFORE_LB
        for i, did in enumerate(self.dot_ids):
            if i < done_in_cycle:
                self.canvas.itemconfig(did, fill=accent, outline=accent)
            else:
                self.canvas.itemconfig(did, fill=TRACK_CLR, outline=TEXT_DIM)

        # Stats
        self.total_label.config(
            text=f"{self.pomodoros}  pomodoro{'s' if self.pomodoros != 1 else ''}  completed"
        )

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _accent(self):
        return {"work": ACCENT_WORK, "short": ACCENT_SB, "long": ACCENT_LB}[self.mode]

    def _set_btn_state(self, btn: tk.Label, disabled: bool, accent: str):
        if disabled:
            btn.config(fg=TEXT_DIM, bg=PANEL, state="disabled")
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
        else:
            btn.config(fg=accent, bg=PANEL, state="normal")
            btn.bind("<Enter>", lambda e, b=btn, a=accent: b.config(bg=a, fg=BG))
            btn.bind("<Leave>", lambda e, b=btn, a=accent: b.config(bg=PANEL, fg=a))

    def _flash_canvas(self, times: int):
        """Brief flash animation to signal session end."""
        if times <= 0:
            self.root.configure(bg=BG)
            return
        flash_clr = self._accent()
        self.root.configure(bg=flash_clr)
        self.root.after(120, lambda: self.root.configure(bg=BG))
        self.root.after(240, lambda: self._flash_canvas(times - 1))

    def _play_work_end(self):
        """Ascending chime — work session done, enjoy your break!"""
        for freq in [880, 1100, 1320]:
            _beep(freq, 150)

    def _play_break_end(self):
        """Two short beeps — break over, time to focus."""
        for freq in [660, 880]:
            _beep(freq, 200)


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PomodoroTimer()

