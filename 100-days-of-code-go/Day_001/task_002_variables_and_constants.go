// Variables
package main

import "fmt"

func main() {
	// Variable declaration with explicit type
	var name string = "Alice"
	var age int = 30
	var name1 = "Bob" // Type inferred as string

	city := "New York" // Short variable declaration
	count:= 10         // Type inferred as int

	// Default values:

	//Numeric types: 0
	// Boolean Types: false
	// String Types: ""
	// Pointers, slices, maps, channels, interfaces: nil

	// Constants
	const pi = 3.14
	const GRAVITY = 9.81
	const days int = 7

	const {
		monday = 1
		tuesday = 2
		wednesday = 3 // untyped constant
		thursday int = 4 // typed constant
	}
}