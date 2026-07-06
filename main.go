package main

import (
	"fmt"
	"math/rand/v2"
	"os"
	"runtime"
	"sync"
	"time"
)

func main() {
	// 1. Узнаем, сколько ядер есть в твоем Mac
	numCores := runtime.NumCPU()

	// Отправляем в Python команду инициализации экранов
	fmt.Printf("init:%d\n", numCores)

	// WaitGroup нужен, чтобы main() не закрылся раньше, чем горутины сделают работу
	var wg sync.WaitGroup

	// 2. Запускаем по одной горутине на каждое доступное ядро
	for coreID := 1; coreID <= numCores; coreID++ {
		wg.Add(1)

		// Запускаем горутину, передавая ей уникальный ID "ядра"
		go func(id int) {
			defer wg.Done()

			// Каждая горутина делает работу со своей случайной скоростью
			totalSteps := 100
			speed := 50 + rand.IntN(150) // задержка в миллисекундах

			// Внутри горутины в main.go:
			for step := 1; step <= totalSteps; step++ {
				time.Sleep(time.Duration(speed) * time.Millisecond)

				// Отправляем прогресс
				fmt.Printf("progress:%d:%d\n", id, step)

				// 🔥 ДОБАВЬТЕ ЭТУ СТРОЧКУ СЮДА:
				os.Stdout.Sync() // Принудительно выталкивает байты в Python прямо сейчас!
			}

			// Сигнализируем Python, что это ядро освободилось
			fmt.Printf("done:%d\n", id)
		}(coreID)
	}

	// Ждем окончания работы всех горутин
	wg.Wait()
	fmt.Println("all_done")
}
