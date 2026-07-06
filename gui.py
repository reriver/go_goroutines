import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk

class GoVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Go Goroutines Core Monitor")
        self.progress_bars = {}
        self.labels = {}
        
        # Запускаем чтение бэкенда в отдельном потоке Python,
        # чтобы графическое окно не зависало
        threading.Thread(target=self.read_go_output, daemon=True).start()

    def read_go_output(self):
        # Запускаем наш скомпилированный Go-бинарник
        process = subprocess.Popen(
            ["./go_backend"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )

        # Построчно читаем то, что Go пишет в Stdout через fmt.Println
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            parts = line.split(":")
            command = parts[0]

            if command == "init":
                # Получили команду инициализации ядер (например, init:8)
                cores_count = int(parts[1])
                # Вызываем отрисовку интерфейса в главном потоке Python
                self.root.after(0, self.setup_ui, cores_count)

            elif command == "progress":
                # Получили прогресс (progress:НомерЯдра:Процент)
                core_id = int(parts[1])
                value = int(parts[2])
                self.root.after(0, self.update_progress, core_id, value)

            elif command == "done":
                core_id = int(parts[1])
                self.root.after(0, self.mark_done, core_id)

    def setup_ui(self, cores_count):
        print(f"Инициализируем интерфейс под {cores_count} ядер Mac...")
        for i in range(1, cores_count + 1):
            frame = ttk.Frame(self.root, padding=10)
            frame.pack(fill=tk.X)

            label = ttk.Label(frame, text=f"Ядро CPU #{i}: РАБОТАЕТ", width=35)
            label.pack(side=tk.LEFT)
            self.labels[i] = label

            progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
            progress.pack(side=tk.LEFT, padx=10)
            self.progress_bars[i] = progress

    def update_progress(self, core_id, value):
        if core_id in self.progress_bars:
            self.progress_bars[core_id]['value'] = value
            self.labels[core_id].config(text=f"Ядро CPU #{core_id}: Вычисление {value}%")

    def mark_done(self, core_id):
        if core_id in self.labels:
            self.labels[core_id].config(text=f"Ядро CPU #{core_id}: СВОБОДНО (Done)")

if __name__ == "__main__":
    root = tk.Tk()
    app = GoVisualizer(root)
    root.mainloop()