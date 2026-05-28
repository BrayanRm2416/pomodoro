# -*- coding: utf-8 -*-
"""
NERV STUDY SYSTEM  ///  Evangelion-style Pomodoro Timer
"""
import tkinter as tk
import math

try:
    import winsound
    def _beep(f, d): winsound.Beep(f, d)
except ImportError:
    def _beep(f, d): pass

# ═══════════════════════════════ PALETTE ════════════════════════════════════
BG       = "#020b18"
PANEL    = "#060e1f"
HEX_C    = "#081828"
ORANGE   = "#ff6600"
ORANGE_D = "#7a3200"
CYAN_N   = "#00e5ff"
GREEN_N  = "#39ff14"
AMBER    = "#ffb300"
RED_W    = "#ff2233"
TEXT_W   = "#dde8f5"
TEXT_D   = "#1e3550"
SCAN_C   = "#002244"

MC  = {"work": ORANGE,  "short": CYAN_N,  "long": GREEN_N}
MJ  = {"work": "フォーカス",  "short": "ブレイク",  "long": "ロングブレイク"}
ME  = {"work": "FOCUS SESSION",  "short": "SHORT BREAK",  "long": "LONG BREAK"}

WIN_W, WIN_H = 500, 715
CX = WIN_W // 2
CVH = 418
CY  = CVH // 2 + 15
R   = 146
AW  = 11

D_WORK = 25 * 60
D_SB   =  5 * 60
D_LB   = 15 * 60
N_CYCS = 4

MSGS = [
    "◈  DEJA TU MÓVIL LEJOS  ◈",
    "◈  TEN AGUA A LA MANO  ◈",
    "◈  SILENCIA NOTIFICACIONES  ◈",
    "◈  ELIMINA DISTRACCIONES  ◈",
    "◈  UN PASO A LA VEZ  —  AVANZAS  ◈",
    "◈  TU FUTURO TE LO AGRADECERÁ  ◈",
    "◈  MODO FOCUS ACTIVO  //  NERV  ◈",
]


class NervTimer:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NERV  //  STUDY SYSTEM")
        self.root.geometry(f"{WIN_W}x{WIN_H}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.work_time   = D_WORK
        self.short_break = D_SB
        self.long_break  = D_LB
        self.mode        = "work"
        self.is_running  = False
        self.after_id    = None
        self.pomodoros   = 0
        self.time_left   = D_WORK
        self.total_time  = D_WORK

        self._scan_y   = 0
        self._pulse    = 0.0
        self._blink    = True
        self._msg_i    = 0
        self._msg_c    = 0
        self._msg_hold = 0

        self._build_header()
        self._build_canvas()
        self._build_settings()
        self._build_buttons()
        self._build_ticker()
        self._build_footer()

        self._update_display()
        self._anim_loop()
        self._anim_blink()
        self._anim_message()

        self.root.mainloop()

    # ── header ───────────────────────────────────────────────────────────
    def _build_header(self):
        hf = tk.Frame(self.root, bg=BG, height=48)
        hf.pack(fill="x")

        tk.Label(hf, text="⚠ ⚠", font=("Courier", 10, "bold"),
                 fg=ORANGE_D, bg=BG).place(x=12, y=14)

        tk.Label(hf, text="NERV  //  STUDY  SYSTEM",
                 font=("Courier", 13, "bold"), fg=ORANGE, bg=BG).place(
                 relx=0.5, y=10, anchor="n")

        tk.Label(hf, text="神経  研究モジュール",
                 font=("Courier", 8), fg=ORANGE_D, bg=BG).place(
                 relx=0.5, y=30, anchor="n")

        self._status_dot = tk.Label(hf, text="●", font=("Courier", 12),
                                    fg=GREEN_N, bg=BG)
        self._status_dot.place(x=WIN_W - 30, y=14)

        sep = tk.Canvas(self.root, width=WIN_W, height=2, bg=BG,
                        highlightthickness=0)
        sep.pack()
        sep.create_line(0, 1, WIN_W, 1, fill=ORANGE_D, width=1)
        for x in range(0, WIN_W, 8):
            sep.create_line(x, 1, x + 4, 1, fill=ORANGE, width=1)

    # ── main canvas ──────────────────────────────────────────────────────
    def _build_canvas(self):
        self.cv = tk.Canvas(self.root, width=WIN_W, height=CVH,
                            bg=BG, highlightthickness=0)
        self.cv.pack()

        self._draw_hex_grid()

        self._scan_item = self.cv.create_rectangle(
            0, 0, WIN_W, 6, fill=SCAN_C, outline="", stipple="gray50")

        for i in range(60):
            ang = math.radians(i * 6 - 90)
            r_in  = R + AW + 6  if i % 5 == 0 else R + AW + 4
            r_out = R + AW + 14 if i % 5 == 0 else R + AW + 9
            clr   = TEXT_D if i % 5 != 0 else ORANGE_D
            x1 = CX + r_in  * math.cos(ang)
            y1 = CY + r_in  * math.sin(ang)
            x2 = CX + r_out * math.cos(ang)
            y2 = CY + r_out * math.sin(ang)
            self.cv.create_line(x1, y1, x2, y2, fill=clr,
                                width=2 if i % 5 == 0 else 1)

        for dr, clr, w in [(R + AW + 22, TEXT_D, 1), (R + AW + 25, ORANGE_D, 1)]:
            self.cv.create_oval(CX-dr, CY-dr, CX+dr, CY+dr, outline=clr, width=w)

        self.cv.create_oval(CX-R, CY-R, CX+R, CY+R,
                            outline=TEXT_D, width=AW)

        self._arc = self.cv.create_arc(
            CX-R, CY-R, CX+R, CY+R,
            start=90, extent=0,
            outline=ORANGE, width=AW, style=tk.ARC)

        self._halo = self.cv.create_oval(
            CX-8, CY-R-8, CX+8, CY-R+8,
            fill="", outline=ORANGE, width=2)

        self._dot = self.cv.create_oval(
            CX-5, CY-R-5, CX+5, CY-R+5,
            fill=ORANGE, outline="")

        self._brackets = []
        for _ in range(4):
            ln = self.cv.create_line(0, 0, 0, 0, fill=ORANGE, width=2,
                                     capstyle=tk.ROUND)
            self._brackets.append(ln)
        self._draw_brackets(0)

        self.cv.create_text(CX, CY - 70, text="NERV",
                            font=("Courier", 9, "bold"),
                            fill=ORANGE_D, anchor="center")
        self.cv.create_text(CX, CY - 58, text="───────────",
                            font=("Courier", 8), fill=TEXT_D, anchor="center")

        self._jp_label = self.cv.create_text(
            CX, CY - 42, text=MJ["work"],
            font=("Courier", 11, "bold"), fill=ORANGE, anchor="center")

        self._en_label = self.cv.create_text(
            CX, CY - 24, text=ME["work"],
            font=("Courier", 8), fill=ORANGE_D, anchor="center")

        self._timer_text = self.cv.create_text(
            CX, CY + 18, text="25:00",
            font=("Courier", 56, "bold"), fill=TEXT_W, anchor="center")

        self._sub_text = self.cv.create_text(
            CX, CY + 65, text=f"SESSION  1  /  {N_CYCS}",
            font=("Courier", 10), fill=TEXT_D, anchor="center")

        self._dot_ids = []
        spacing = 24
        start_x = CX - (N_CYCS - 1) * spacing / 2
        for i in range(N_CYCS):
            x = start_x + i * spacing
            y = CY + 95
            d = self.cv.create_oval(x-6, y-6, x+6, y+6,
                                    fill=TEXT_D, outline=ORANGE_D, width=1)
            self._dot_ids.append(d)

        self._left_info = self.cv.create_text(
            18, CY - 10, text="SYS\n━━━\nACT\nIVE", anchor="w",
            font=("Courier", 7), fill=TEXT_D, justify="left")
        self._right_info = self.cv.create_text(
            WIN_W - 18, CY - 10, text="EVA\n━━━\nUNIT\n-01", anchor="e",
            font=("Courier", 7), fill=TEXT_D, justify="right")

        self.cv.create_line(30, CVH - 4, WIN_W - 30, CVH - 4,
                            fill=ORANGE_D, width=1)

    def _draw_hex_grid(self):
        hr = 30
        hh = hr * math.sqrt(3)
        cols = int(WIN_W / (hr * 1.5)) + 3
        rows = int(CVH / hh) + 3
        for row in range(rows):
            for col in range(cols):
                hcx = col * hr * 3 + (hr * 1.5 if row % 2 else 0) - hr
                hcy = row * hh - hh / 2
                pts = []
                for i in range(6):
                    ang = math.radians(60 * i + 30)
                    pts.extend([hcx + hr * math.cos(ang),
                                 hcy + hr * math.sin(ang)])
                self.cv.create_polygon(pts, outline=HEX_C, fill="", width=1)

    def _draw_brackets(self, offset: float):
        bx1 = CX - R - 30 + offset
        by1 = CY - R - 30 + offset
        bx2 = CX + R + 30 - offset
        by2 = CY + R + 30 - offset
        L   = 26
        accent = MC[self.mode]
        coords = [
            (bx1, by1 + L, bx1, by1, bx1 + L, by1),
            (bx2 - L, by1, bx2, by1, bx2, by1 + L),
            (bx1, by2 - L, bx1, by2, bx1 + L, by2),
            (bx2 - L, by2, bx2, by2, bx2, by2 - L),
        ]
        for lid, pts in zip(self._brackets, coords):
            self.cv.coords(lid, *pts)
            self.cv.itemconfig(lid, fill=accent)

    # ── settings ─────────────────────────────────────────────────────────
    def _build_settings(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="x", padx=20, pady=(4, 2))

        labels   = ["FOCUS", "S.BREAK", "L.BREAK"]
        attrs    = ["work_time", "short_break", "long_break"]
        colors   = [ORANGE, CYAN_N, GREEN_N]
        defaults = [25, 5, 15]
        self._svars = []

        for col, (lbl, attr, clr, dflt) in enumerate(
                zip(labels, attrs, colors, defaults)):
            cf = tk.Frame(outer, bg=PANEL, padx=10, pady=6)
            cf.grid(row=0, column=col, padx=6, sticky="ew")
            outer.columnconfigure(col, weight=1)

            tk.Label(cf, text=lbl, font=("Courier", 8, "bold"),
                     fg=clr, bg=PANEL).pack()
            var = tk.IntVar(value=dflt)
            self._svars.append((attr, var))
            spin = tk.Spinbox(
                cf, from_=1, to=90, textvariable=var, width=4,
                font=("Courier", 12, "bold"), fg=clr, bg=BG,
                insertbackground=clr, relief="flat", justify="center",
                buttonbackground=PANEL,
                command=lambda a=attr, v=var: self._on_setting_change(a, v))
            spin.pack()
            tk.Label(cf, text="min", font=("Courier", 7),
                     fg=TEXT_D, bg=PANEL).pack()

    def _on_setting_change(self, attr: str, var: tk.IntVar):
        setattr(self, attr, max(1, var.get()) * 60)
        if not self.is_running:
            self.time_left  = self.work_time
            self.total_time = self.work_time
            self._update_display()

    # ── buttons ───────────────────────────────────────────────────────────
    def _build_buttons(self):
        bf = tk.Frame(self.root, bg=BG)
        bf.pack(pady=(6, 4))

        self._btn_start = self._pill(bf, "▶  START",  self.start_timer, ORANGE,  0, 0)
        self._btn_pause = self._pill(bf, "⏸  PAUSE",  self.pause_timer, CYAN_N,  0, 1)
        self._btn_reset = self._pill(bf, "↺  RESET",  self.reset_timer, GREEN_N, 0, 2)
        self._set_btn(self._btn_pause, disabled=True, accent=CYAN_N)

    def _pill(self, parent, text, cmd, accent, row, col):
        btn = tk.Label(parent, text=text, font=("Courier", 10, "bold"),
                       fg=accent, bg=PANEL, width=11, pady=8,
                       relief="flat", cursor="hand2")
        btn.grid(row=row, column=col, padx=6)
        btn.bind("<Button-1>", lambda e: cmd())
        btn.bind("<Enter>",    lambda e, b=btn, a=accent: b.config(bg=a, fg=BG))
        btn.bind("<Leave>",    lambda e, b=btn, a=accent: b.config(bg=PANEL, fg=a))
        return btn

    def _set_btn(self, btn, disabled: bool, accent: str):
        if disabled:
            btn.config(fg=TEXT_D, bg=PANEL, state="disabled")
            btn.unbind("<Enter>"); btn.unbind("<Leave>")
        else:
            btn.config(fg=accent, bg=PANEL, state="normal")
            btn.bind("<Enter>", lambda e, b=btn, a=accent: b.config(bg=a, fg=BG))
            btn.bind("<Leave>", lambda e, b=btn, a=accent: b.config(bg=PANEL, fg=a))

    # ── ticker ────────────────────────────────────────────────────────────
    def _build_ticker(self):
        tf = tk.Frame(self.root, bg=PANEL, height=30)
        tf.pack(fill="x", padx=0, pady=(2, 0))

        tk.Label(tf, text="//", font=("Courier", 9, "bold"),
                 fg=ORANGE_D, bg=PANEL).pack(side="left", padx=(10, 4))

        self._ticker_lbl = tk.Label(tf, text="", font=("Courier", 9),
                                    fg=AMBER, bg=PANEL, anchor="w")
        self._ticker_lbl.pack(side="left", fill="x", expand=True, pady=5)

        tk.Label(tf, text="//", font=("Courier", 9, "bold"),
                 fg=ORANGE_D, bg=PANEL).pack(side="right", padx=(4, 10))

    # ── footer ────────────────────────────────────────────────────────────
    def _build_footer(self):
        ff = tk.Frame(self.root, bg=BG)
        ff.pack(fill="x", padx=20, pady=(4, 6))

        tk.Label(ff, text="TODAY", font=("Courier", 7, "bold"),
                 fg=TEXT_D, bg=BG).pack(side="left")

        self._stats_lbl = tk.Label(
            ff, text="0  POMODOROS  COMPLETED",
            font=("Courier", 9, "bold"), fg=TEXT_W, bg=BG)
        self._stats_lbl.pack(side="left", padx=12)

        self._wave_lbl = tk.Label(ff, text="", font=("Courier", 9),
                                  fg=ORANGE_D, bg=BG)
        self._wave_lbl.pack(side="right")

    # ══════════════════════════ TIMER LOGIC ══════════════════════════════

    def start_timer(self):
        if self.is_running: return
        self.is_running = True
        self._set_btn(self._btn_start, disabled=True,  accent=ORANGE)
        self._set_btn(self._btn_pause, disabled=False, accent=CYAN_N)
        self._tick()

    def pause_timer(self):
        if not self.is_running: return
        self.is_running = False
        if self.after_id: self.root.after_cancel(self.after_id)
        self._set_btn(self._btn_start, disabled=False, accent=ORANGE)
        self._set_btn(self._btn_pause, disabled=True,  accent=CYAN_N)

    def reset_timer(self):
        self.is_running = False
        if self.after_id: self.root.after_cancel(self.after_id)
        self.mode       = "work"
        self.time_left  = self.work_time
        self.total_time = self.work_time
        self._set_btn(self._btn_start, disabled=False, accent=ORANGE)
        self._set_btn(self._btn_pause, disabled=True,  accent=CYAN_N)
        self._update_display()

    def _tick(self):
        if not self.is_running: return
        if self.time_left > 0:
            self.time_left -= 1
            self._update_display()
            self.after_id = self.root.after(1000, self._tick)
        else:
            self._session_complete()

    def _session_complete(self):
        self.is_running = False
        if self.mode == "work":
            self.pomodoros += 1
            for f in [880, 1100, 1320]: _beep(f, 150)
            if self.pomodoros % N_CYCS == 0:
                self.mode, self.time_left, self.total_time = \
                    "long", self.long_break, self.long_break
            else:
                self.mode, self.time_left, self.total_time = \
                    "short", self.short_break, self.short_break
        else:
            for f in [660, 880]: _beep(f, 180)
            self.mode, self.time_left, self.total_time = \
                "work", self.work_time, self.work_time

        self._set_btn(self._btn_start, disabled=False, accent=ORANGE)
        self._set_btn(self._btn_pause, disabled=True,  accent=CYAN_N)
        self._flash(4)
        self._update_display()

    # ══════════════════════════ DISPLAY ══════════════════════════════════

    def _update_display(self):
        accent = MC[self.mode]
        m, s   = divmod(self.time_left, 60)

        self.cv.itemconfig(self._timer_text, text=f"{m:02d}:{s:02d}")

        ratio  = self.time_left / max(self.total_time, 1)
        extent = -360 * ratio
        self.cv.itemconfig(self._arc, extent=extent, outline=accent)

        self.cv.itemconfig(self._jp_label, text=MJ[self.mode], fill=accent)
        self.cv.itemconfig(self._en_label, text=ME[self.mode], fill=accent)

        n_in_cycle = (self.pomodoros % N_CYCS) + (1 if self.mode == "work" else 0)
        self.cv.itemconfig(self._sub_text,
                           text=f"SESSION  {n_in_cycle}  /  {N_CYCS}")

        done = self.pomodoros % N_CYCS
        for i, did in enumerate(self._dot_ids):
            if i < done:
                self.cv.itemconfig(did, fill=accent, outline=accent)
            else:
                self.cv.itemconfig(did, fill=TEXT_D, outline=ORANGE_D)

        n = self.pomodoros
        self._stats_lbl.config(
            text=f"{n}  POMODORO{'S' if n != 1 else ''}  COMPLETED")

        bars = int(ratio * 10)
        self._wave_lbl.config(
            text="█" * bars + "░" * (10 - bars), fg=accent)

    # ══════════════════════════ ANIMATIONS ═══════════════════════════════

    def _anim_loop(self):
        # scan line
        self._scan_y += 4
        if self._scan_y > CVH:
            self._scan_y = 0
        self.cv.coords(self._scan_item,
                       0, self._scan_y, WIN_W, self._scan_y + 5)

        # pulse
        self._pulse = (self._pulse + 0.12) % (2 * math.pi)
        pulse_r = 7 + 3 * math.sin(self._pulse)

        # glow dot
        ratio = self.time_left / max(self.total_time, 1)
        angle = math.radians(90 - 360 * (1 - ratio))
        gx = CX + R * math.cos(angle)
        gy = CY - R * math.sin(angle)
        accent = MC[self.mode]

        self.cv.coords(self._dot, gx-5, gy-5, gx+5, gy+5)
        self.cv.itemconfig(self._dot, fill=accent)

        hr = pulse_r + 4
        self.cv.coords(self._halo, gx-hr, gy-hr, gx+hr, gy+hr)
        self.cv.itemconfig(self._halo, outline=accent)

        # corner brackets oscillate
        brk_off = 2 * math.sin(self._pulse * 0.5)
        self._draw_brackets(brk_off)

        # side data flicker
        if int(self._pulse * 3) % 20 == 0:
            info_clr = MC[self.mode] if self.is_running else TEXT_D
            self.cv.itemconfig(self._left_info,  fill=info_clr)
            self.cv.itemconfig(self._right_info, fill=info_clr)

        self.root.after(30, self._anim_loop)

    def _anim_blink(self):
        self._blink = not self._blink
        clr = GREEN_N if (self._blink and self.is_running) else \
              (ORANGE_D if not self.is_running else GREEN_N)
        self._status_dot.config(fg=clr if self._blink else TEXT_D)
        self.root.after(550, self._anim_blink)

    def _anim_message(self):
        msg = MSGS[self._msg_i]

        if self._msg_hold > 0:
            self._msg_hold -= 1
            delay = 80
        elif self._msg_c < len(msg):
            self._msg_c += 1
            self._ticker_lbl.config(text=msg[:self._msg_c])
            if self._msg_c == len(msg):
                self._msg_hold = 30
            delay = 55
        else:
            self._msg_c = 0
            self._ticker_lbl.config(text="")
            self._msg_i = (self._msg_i + 1) % len(MSGS)
            delay = 400

        self.root.after(delay, self._anim_message)

    def _flash(self, n: int):
        if n <= 0:
            self.root.configure(bg=BG); return
        clr = MC[self.mode]
        self.root.configure(bg=clr)
        self.root.after(100, lambda: self.root.configure(bg=BG))
        self.root.after(200, lambda: self._flash(n - 1))


if __name__ == "__main__":
    NervTimer()
