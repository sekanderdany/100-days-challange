//Below are all the data types in Go programming language along with examples.

package main

import "fmt"

func main() {
	// Integers
	// Floating Point Numbers
	// Complex Numbers
	// Characters (rune)
	// Strings
	// Constants
	// Pointers
	// Time
	// Errors
	// Booleans
	// Arrays
	// Slices
	// Maps
	// Structs 
	// Functions
	// Channels
	// JSON
	// Text and HTML Templates

	// EXAMPLES:

	// Integers
	var intVar int = 42
	var int8Var int8 = 10
	var int16Var int16 = 1000
	var int32Var int32 = 100000
	var int64Var int64 = 10000000
	var uintVar uint = 42

	// Floating Point Numbers
	var float32Var float32 = 3.14
	var float64Var float64 = 2.71828

	// Complex Numbers
	var complexVar complex128 = 1 + 2i

	// Characters (rune)
	var runeVar rune = 'A'

	// Strings
	var stringVar string = "Hello, Go!"

	// Constants
	const constantVar = 100

	// Pointers
	var pointerVar *int = &intVar

	// Booleans
	var boolVar bool = true

	// Arrays
	var arrayVar [3]int = [3]int{1, 2, 3}

	// Slices
	var sliceVar []int = []int{1, 2, 3, 4, 5}

	// Maps
	var mapVar map[string]int = map[string]int{"a": 1, "b": 2}

	// Structs
	type Person struct {
		Name string
		Age  int
	}
	var structVar Person = Person{"Alice", 30}

	// Functions
	fn := func(x int) int { return x * 2 }

	// Channels, JSON, Text and HTML Templates are more advanced topics and typically require more context to demonstrate effectively.
	// Print all variables
	fmt.Println("Integer:", intVar)
	fmt.Println("Float:", float64Var)
	fmt.Println("Complex:", complexVar)
	fmt.Println("Rune:", string(runeVar))
	fmt.Println("String:", stringVar)
	fmt.Println("Constant:", constantVar)
	fmt.Println("Pointer:", pointerVar)
	fmt.Println("Boolean:", boolVar)
	fmt.Println("Array:", arrayVar)
	fmt.Println("Slice:", sliceVar)
	fmt.Println("Map:", mapVar)
	fmt.Println("Struct:", structVar)
	fmt.Println("Function result:", fn(5))
}