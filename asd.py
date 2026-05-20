import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


work_time= 25 * 60
short_break = 10 * 60
long_break = 25 * 60

class PomodoroTimer():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pomodoro Timer")

        self.start_button = ttk.Button(self. root, text="Start", command=self.start_timer)
        self.start_button.pack(pady=5)
        self.stop_button = ttk.Button(self. root, text="Stop", command=self.stop_timer,
                  state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.work_time, self.short_break = work_time, short_break
        self.is_work_work_time, self.pomodoro_completed, self.is_running = True, 0, False
        self.root.mainloop()

    def start_timer(self):
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.is_running = True
        self.update_timer()

    def stop_timer(self):
        self.stop_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.is_running = False





root = tk.Tk()
app = PomodoroTimer()
root.mainloop()