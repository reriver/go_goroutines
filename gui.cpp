#include <GLFW/glfw3.h>
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
#include <map>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <thread>

const int COLS = 150;
const int ROWS = 75;
const int BLOCK_SIZE = 8;
const int TOTAL_JOBS = 11250;

// Структура цвета для OpenGL (значения от 0.0 до 1.0)
struct RGB {
    float r, g, b;
};

const RGB BG_COLOR = {0.12f, 0.12f, 0.12f};   // Темно-серый
const RGB DONE_COLOR = {0.23f, 0.23f, 0.23f}; // Серый выполненный

std::map<int, RGB> CORE_COLORS = {
    {1, {1.0f, 0.2f, 0.2f}},  // Красный
    {2, {0.2f, 1.0f, 0.2f}},  // Зеленый
    {3, {0.2f, 0.4f, 1.0f}},  // Синий
    {4, {1.0f, 1.0f, 0.2f}},  // Желтый
    {5, {1.0f, 0.2f, 1.0f}},  // Пурпурный
    {6, {0.2f, 1.0f, 1.0f}},  // Циан
    {7, {1.0f, 0.6f, 0.2f}},  // Оранжевый
    {8, {0.6f, 0.2f, 1.0f}}   // Фиолетовый
};

// Монолитный вектор цветов в памяти — идеальная кэш-локальность для M1
std::vector<RGB> matrix_colors(TOTAL_JOBS, BG_COLOR);

// Сверхбыстрый нативный поток для чтения UDP-сокетов
void udp_listen_thread() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        std::cerr << "Ошибка создания сокета" << std::endl;
        return;
    }
    
    sockaddr_in server_addr{};
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(10002);
    server_addr.sin_addr.s_addr = INADDR_ANY;

    if (bind(sock, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "Ошибка bind сокета на порт 10002" << std::endl;
        close(sock);
        return;
    }

    char buffer[4096];
    while (true) {
        int bytes_received = recv(sock, buffer, sizeof(buffer) - 1, 0);
        if (bytes_received <= 0) continue;
        
        buffer[bytes_received] = '\0';
        std::string msg(buffer);
        std::stringstream ss(msg);
        std::string line;

        while (std::getline(ss, line)) {
            if (line.empty()) continue;
            
            if (line.rfind("start:", 0) == 0) {
                int job_id, core_id;
                char colon;
                std::stringstream ls(line.substr(6));
                ls >> job_id >> colon >> core_id;
                if (job_id >= 0 && job_id < TOTAL_JOBS) {
                    matrix_colors[job_id] = CORE_COLORS[core_id];
                }
            } else if (line.rfind("done:", 0) == 0) {
                int job_id;
                std::stringstream ls(line.substr(5));
                ls >> job_id;
                if (job_id >= 0 && job_id < TOTAL_JOBS) {
                    matrix_colors[job_id] = DONE_COLOR;
                }
            }
        }
    }
    close(sock);
}

int main() {
    // 1. Инициализируем графический движок GLFW
    if (!glfwInit()) return -1;

    // Считаем точные размеры окна
    int width = COLS * BLOCK_SIZE;
    int height = ROWS * BLOCK_SIZE;

    GLFWwindow* window = glfwCreateWindow(width, height, "Go-to-C++ Ultra UDP Monitor", NULL, NULL);
    if (!window) {
        glfwTerminate();
        return -1;
    }

    glfwMakeContextCurrent(window);
    
    // Включаем вертикальную синхронизацию (V-Sync на 60 кадров), чтобы не греть чип M1
    glfwSwapInterval(1);

    // Настраиваем двумерную систему координат под размер нашей сетки
    glViewport(0, 0, width, height);
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, width, height, 0, -1, 1);
    glMatrixMode(GL_MODELVIEW);
    glLoadIdentity();

    // 2. Запускаем параллельный поток чтения сокетов
    std::thread(udp_listen_thread).detach();

    // 3. Главный графический цикл рендеринга
    while (!glfwWindowShouldClose(window)) {
        // Очищаем экран глубоким темным цветом
        glClearColor(0.06f, 0.06f, 0.06f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);

        // Отрисовываем 11 250 квадратов на максимальной скорости GPU
        for (int job_id = 0; job_id < TOTAL_JOBS; ++job_id) {
            int row = job_id / COLS;
            int col = job_id % COLS;

            float x = col * BLOCK_SIZE;
            float y = row * BLOCK_SIZE;

            RGB color = matrix_colors[job_id];

            // Рисуем квадрат через графический конвейер OpenGL
            glBegin(GL_QUADS);
            glColor3f(color.r, color.g, color.b);
            glVertex2f(x, y);
            glVertex2f(x + BLOCK_SIZE - 1, y);
            glVertex2f(x + BLOCK_SIZE - 1, y + BLOCK_SIZE - 1);
            glVertex2f(x, y + BLOCK_SIZE - 1);
            glEnd();
        }

        // Выталкиваем готовый кадр на экран Mac M1
        glfwSwapBuffers(window);
        glfwPollEvents();
    }

    glfwTerminate();
    return 0;
}
