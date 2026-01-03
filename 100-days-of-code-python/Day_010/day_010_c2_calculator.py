'''
TODO 1: Ask user for a number
TODO 2: Ask the user for a mathematical operation (+, -, *, /)
TODO 3: Ask user for next number
TODO 4: Perform calculation and show the two numbers and operator and then equals to result
TODO 5: Ask if they want to continue calculating with the result
'''

def add(n1, n2):
    return n1 + n2
def subtract(n1, n2):
    return n1 - n2
def multiply(n1, n2):
    return n1 * n2
def divide(n1, n2):
    return n1 / n2
operations = {
    "+": add,
    "-": subtract,
    "*": multiply,
    "/": divide
}

def calculator():
    num1 = float(input("Enter first number: "))
    for symbol in operations:
        print(symbol)
    should_continue = True
    while should_continue:
        operation_symbol = input("Pick an operation from the line above: ")
        num2 = float(input("Enter next number: "))
        calculation_function = operations[operation_symbol]
        answer = calculation_function(num1, num2)
        print(f"{num1} {operation_symbol} {num2} = {answer}")
        next_step = input(f"Type 'y' to continue calculating with {answer}, or type 'n' to start a new calculation: ")
        if next_step == 'y':
            num1 = answer
        else:
            should_continue = False
            calculator()
calculator()