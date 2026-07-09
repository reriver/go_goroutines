import subprocess
import threading
import tkinter as tk
from tkinter import ttk
import os
import time  # Добавили пакет времени для разгрузки процессора

class SmoothPixelVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Go Channels 11,250 Goroutines Matrix")
        
        # Крупные сочные квадраты 8x8 пикселей
        self.block_size = 8
        self.cols = 150
        self.rows = 75
        self.width = self.cols * self.block_size
        self.height = self.rows * self.block_size
        
        # Создаем холст
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#111111", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)
        
        self.pixels = {}
        
        # Сверх-яркая неоновая палитра для 8 ядер чипа M1
        self.core_colors = {
            1: "#FF3333",  # Ярко-красный
            2: "#33FF33",  # Неоновый зеленый
            3: "#3366FF",  # Электрик синий
            4: "#FFFF33",  # Кислотно-желтый
            5: "#FF33FF",  # Пурпурный
            6: "#33FFFF",  # Бирюзовый
            7: "#FF9933",  # Солнечно-оранжевый
            8: "#9933FF"   # Глубокий фиолетовый
        }
        self.done_color = "#3a3a3a"  # Спокойный серый для выполненных задач

        # Отрисовываем сетку крупных "спящих" горутин
        self.init_matrix()

        # Запускаем чтение бэкенда Go
        threading.Thread(target=self.read_go_output, daemon=True).start()

    def init_matrix(self):
        for job_id in range(11250):
            row = job_id // self.cols
            col = job_id % self.cols
            
            x1 = col * self.block_size
            y1 = row * self.block_size
            x2 = x1 + self.block_size
            y2 = y1 + self.block_size
            
            # outline="" (без обводки) убирает тормоза на Mac
            rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, fill="#1e1e1e", outline="")
            self.pixels[job_id] = rect_id

    def read_go_output(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(current_dir, "go_backend")

        process = subprocess.Popen(
            [backend_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True
        )

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            parts = line.split(":")
            command = parts

            if command == "start":
                job_id = int(parts)
                core_id = int(parts)
                color = self.core_colors.get(core_id, "#ffffff")
                self.root.after(0, self.change_pixel_color, job_id, color)

            elif command == "done":
                job_id = int(parts)
                self.root.after(0, self.change_pixel_color, job_id, self.done_color)
            
            # 🔥 ВОТ ОН, СПАСИТЕЛЬНЫЙ ХАК:
            # Даем графическому потоку Mac 1 миллисекунду на то, чтобы перевести дух и отрисовать интерфейс
            time.sleep(0.001)

    def change_pixel_color(self, job_id, color):
        if job_id in self.pixels:
            rect_id = self.pixels[job_id]
            self.canvas.itemconfig(rect_id, fill=color)
            # Принудительно рендерим кадр в окно macOS
            self.root.update_idletasks()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmoothPixelVisualizer(root)
    root.mainloop()
