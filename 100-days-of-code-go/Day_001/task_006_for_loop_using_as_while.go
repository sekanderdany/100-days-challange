package main

import (
	"fmt"
	"math/rand"
	"time"
)

func main() {
	// simple iteration over a range while loop
	i := 1
	for i <= 5 {
		fmt.Println("Iteration:", i)
		i++
	}
	sum := 0
	// infinite loop with break condition
	for {
		sum += 10
		fmt.Println("Infinite Loop")
		if sum >= 50 {
			break
		}
	}

	num := 1
	for num <= 10 {
		if num%2 == 0 {
			num++
			continue // continue to next iteration but skip the code below
		}
		fmt.Println("Odd Number:", num)
		num++ // increment to avoid infinite loop
	}

	source := rand.NewSource(time.Now().UnixNano())
	random := rand.New(source)

	target := random.Intn(100) + 1 // random number between 1 and 100

	fmt.Println("Guess the number between 1 and 100")
	fmt.Println("Enter your guess:")

	var guess int
	for {
		fmt.Scanln(&guess)
		if guess < target {
			fmt.Println("Too low! Try again:")
		} else if guess > target {
			fmt.Println("Too high! Try again:")
		} else {
			fmt.Println("Congratulations! You guessed the number:", target)
			break
		}
	}
}
