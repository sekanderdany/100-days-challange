# Step 4 - Fixing errors and Watching for Red Lines

try:
    age = int(input("How old are you? "))
except ValueError:
    print("Please enter a valid number.")
    age = int(input("How old are you? "))

'''

# Uncomment Step 1: Uncomment this section and try solving the error

if age > 18:
print("You can drive at age {age}.")
    print("You can drive at age {age}.")

'''

# Solution

# Uncomment Step 2:  
if age >= 18:
    print("You can drive at age {age}.")


# After fixing run the code and input value 'twenty' to see the red line error

