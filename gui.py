import socket
import threading
import pygame
import sys

# Размеры нашей сочной сетки 150x75 (итого 11 250 горутин)
COLS = 150
ROWS = 75
BLOCK_SIZE = 8  # Каждый элемент — идеальный квадрат 8х8 пикселей

WIDTH = COLS * BLOCK_SIZE
HEIGHT = ROWS * BLOCK_SIZE

# Яркая неоновая палитра для 8 ядер чипа M1 (RGB формат)
CORE_COLORS = {
    1: (255, 51, 51),    # Ярко-красный
    2: (51, 255, 51),    # Неоновый зеленый
    3: (51, 102, 255),   # Электрик синий
    4: (255, 255, 51),   # Кислотно-желтый
    5: (255, 51, 255),   # Пурпурный
    6: (51, 255, 255),   # Бирюзовый
    7: (255, 153, 51),   # Солнечно-оранжевый
    8: (153, 51, 255)    # Глубокий фиолетовый
}
BG_COLOR = (30, 30, 30)      # Темно-серый цвет спящей горутины
DONE_COLOR = (58, 58, 58)    # Спокойный серый цвет выполненной задачи

# Хранилище цветов для матрицы (изначально все горутины спят)
matrix_colors = [BG_COLOR] * 11250

def start_udp_server():
    global matrix_colors
    # Создаем UDP-сокет и привязываем его к порту 10002
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 10002))
    print("UDP-сервер запущен на порту 10002 и ждет Go...")

    while True:
        data, _ = sock.recvfrom(4096)
        message = data.decode("utf-8").strip()
        
        # Обрабатываем строки из пакета
        for line in message.split("\n"):
            if not line:
                continue
            
            parts = line.split(":")
            command = parts[0]

            if command == "start":
                job_id = int(parts[1])
                core_id = int(parts[2])
                if 0 <= job_id < 11250:
                    matrix_colors[job_id] = CORE_COLORS.get(core_id, (255, 255, 255))

            elif command == "done":
                job_id = int(parts[1])
                if 0 <= job_id < 11250:
                    matrix_colors[job_id] = DONE_COLOR

def main():
    # Инициализируем графический движок pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Go-to-Python UDP Mesh Monitor (Pygame)")
    
    # Запускаем чтение входящих UDP-пакетов в фоновом потоке
    threading.Thread(target=start_udp_server, daemon=True).start()

    clock = pygame.time.Clock()

    # Главный игровой цикл отрисовки
    while True:
        # Проверяем системные события Mac (чтобы окно можно было закрыть крестиком)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Очищаем холст
        screen.fill((17, 17, 17))

        # Отрисовываем всю матрицу 150х75 за один проход видеокарты
        for job_id in range(11250):
            row = job_id // COLS
            col = job_id % COLS
            
            x = col * BLOCK_SIZE
            y = row * BLOCK_SIZE
            
            color = matrix_colors[job_id]
            
            # Рисуем ровный сочный квадрат с черной микро-обводкой в 1 пиксель
            pygame.draw.rect(screen, color, (x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1))

        # Выталкиваем готовый кадр на экран Mac M1
        pygame.display.flip()
        
        # Ограничиваем скорость отрисовки до 60 кадров в секунду, чтобы не греть Mac
        clock.tick(60)

if __name__ == "__main__":
    main()
