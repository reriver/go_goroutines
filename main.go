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
	numCores := runtime.NumCPU()
	fmt.Printf("init:%d\n", numCores)
	os.Stdout.Sync()

	totalJobs := 11250 // 150x75 сетка
	jobsChannel := make(chan int, totalJobs)

	for i := 0; i < totalJobs; i++ {
		jobsChannel <- i
	}
	close(jobsChannel)

	var wg sync.WaitGroup

	for coreID := 1; coreID <= numCores; coreID++ {
		wg.Add(1)
		go func(cID int) {
			defer wg.Done()
			for jobID := range jobsChannel {
				// Старт задачи — красим в цвет ядра
				fmt.Printf("start:%d:%d\n", jobID, cID)
				os.Stdout.Sync()

				// Даем ядру "подержать" задачу, симулируя Work Stealing и прыжки
				steps := 3 + rand.IntN(3)
				for s := 0; s < steps; s++ {
					time.Sleep(time.Duration(10+rand.IntN(20)) * time.Millisecond)
					// Симулируем случайный прыжок на другое ядро
					if rand.Float32() < 0.3 {
						cID = 1 + rand.IntN(numCores)
						fmt.Printf("start:%d:%d\n", jobID, cID)
						os.Stdout.Sync()
					}
				}

				// Финал задачи — красим в серый
				fmt.Printf("done:%d\n", jobID)
				os.Stdout.Sync()
			}
		}(coreID)
	}
	wg.Wait()
}
