'''
Prime Number Checker
Prime numbers are numbers that can only be cleanly divided by themselves and 1. Wikipedia  

You need to write a function called is_prime() that checks whether if the number passed into it is a prime number or not. It should return True or False.

e.g.

7 is a primer number because it is only divisible by 1 and itself.

But 4 is not a prime number because you can divide it by 1, 2 or 4.

NOTE: 2 is a prime number because it's only divisible by 1 and itself, but 1 is not a prime number because it is only divisible by 1.

Example Input 1
73
Example Output 1
True

Example Input 2
75
Example Output 2
False

'''


def is_prime(num):
    if num <= 1:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


# Test cases
print(is_prime(73))  # Expected output: True
print(is_prime(75))  # Expected output: False
