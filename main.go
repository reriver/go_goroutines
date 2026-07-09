package main

import (
	"fmt"
	"log"
	"math/rand/v2"
	"net"
	"runtime"
	"sync"
)

func main() {
	numCores := runtime.NumCPU()

	// 1. Подключаемся к UDP-порту 10002, где нас будет слушать Python
	remoteAddr, err := net.ResolveUDPAddr("udp", "127.0.0.1:10002")
	if err != nil {
		log.Fatalln(err)
	}
	conn, err := net.DialUDP("udp", nil, remoteAddr)
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	// Отправляем стартовую команду инициализации интерфейса под ядра Mac
	initMsg := fmt.Sprintf("init:%d\n", numCores)
	conn.Write([]byte(initMsg))

	// Было: заполнение по порядку от 0 до 11250
	// Стало: Генерируем случайный (перемешанный) порядок задач!
	totalJobs := 11250
	jobsChannel := make(chan int, totalJobs)

	// Создаем массив и заполняем его числами от 0 до 11249
	shuffled := make([]int, totalJobs)
	for i := 0; i < totalJobs; i++ {
		shuffled[i] = i
	}

	// Перемешиваем массив случайным образом [rand]
	rand.Shuffle(len(shuffled), func(i, j int) {
		shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
	})

	// Засыпаем перемешанные индексы в канал
	for _, id := range shuffled {
		jobsChannel <- id
	}
	close(jobsChannel)

	var wg sync.WaitGroup

	// 3. Запускаем горутины по числу ядер чипа M1
	for coreID := 1; coreID <= numCores; coreID++ {
		wg.Add(1)
		go func(cID int) {
			defer wg.Done()
			for jobID := range jobsChannel {
				// Выстреливаем UDP-пакет: задача СТАРТОВАЛА на ядре cID
				startMsg := fmt.Sprintf("start:%d:%d\n", jobID, cID)
				conn.Write([]byte(startMsg))

				// Имитируем микро-работу, чтобы глаз успел заметить вспышку цвета
				//time.Sleep(time.Duration(20+rand.IntN(30)) * time.Millisecond)

				// Выстреливаем UDP-пакет: задача ЗАВЕРШЕНА
				doneMsg := fmt.Sprintf("done:%d\n", jobID)
				conn.Write([]byte(doneMsg))
			}
		}(coreID)
	}

	wg.Wait()
}
