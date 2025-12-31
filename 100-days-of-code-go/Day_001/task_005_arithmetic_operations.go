package main

import (
	"fmt"
	"math"
)

func main() {
	// Variable declaration
	var a, b int = 10, 5
	var result int

	result = a + b
	fmt.Printf("Addition: %d + %d = %d\n", a, b, result)

	result = a - b
	fmt.Printf("Subtraction: %d - %d = %d\n", a, b, result)

	result = a * b
	fmt.Printf("Multiplication: %d * %d = %d\n", a, b, result)

	result = a / b
	fmt.Printf("Division: %d / %d = %d\n", a, b, result)

	result = a % b
	fmt.Printf("Modulus: %d %% %d = %d\n", a, b, result)

	const p float64 = 22 / 7.0

	fmt.Println("Value of constant p (approx. Pi):", p)

	// Overflow with signed integer
	var maxInt int64 = 92342415234567890
	fmt.Println("Max Int64 value:", maxInt)

	maxInt = maxInt + 1
	fmt.Println("Max Int64 value after increment:", maxInt)

	// Overflow with unsigned integer
	var maxUint uint64 = 255
	fmt.Println("Max Uint64 value:", maxUint)
	maxUint = maxUint + 1
	fmt.Println("Max Uint64 value after increment:", maxUint)

	// Underflow with unsigned integer

	var smallFloat float64 = 1.0e-300
	fmt.Println("Small Float64 value:", smallFloat)
	smallFloat = smallFloat / 1.0e+10
	fmt.Println("Small Float64 value after division:", smallFloat)
	smallFloat = smallFloat / math.MaxFloat64
	fmt.Println("Small Float64 value after dividing by MaxFloat64:", smallFloat)
	
}
