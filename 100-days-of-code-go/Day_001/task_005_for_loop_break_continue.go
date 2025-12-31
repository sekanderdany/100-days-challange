package main

import "fmt"

func main() {
	// simple iteration over a range

	for i := 1; i <= 5; i++ {
		fmt.Println("Iteration:", i)
	}

	// interation over collection
	numbers := []int{10, 20, 30, 40, 50}
	for intex, value := range numbers {
		// %v is used to print value of any type
		// %d is used to print integer values
		fmt.Printf("Index: %v, Value: %d\n", intex, value)
	}

	// break statement
	for i := 1; i <= 10; i++ {
		if i%2 == 0 {
			continue // continue to next iteration but skip the code below
		}
		fmt.Println("Odd Number:", i)
		if i >= 7 {
			break // exit the loop
		}
	}

	rows := 5
	// outer loop for Christmas tree
	for i := 1; i <= rows; i++ {
		// print spaces for alignment
		for j := 1; j <= rows-i; j++ {
			fmt.Print(" ")
		}
		// inner loop for asterisks (2*i-1 asterisks per row)
		for k := 1; k <= 2*i-1; k++ {
			fmt.Print("*")
		}
		fmt.Println()
	}

	for i := range 10 {
		fmt.Println(1 - -i)
	}
	fmt.Println("Loop complete")
}
