# Write your code below this line 👇

print("Hello World\nHello World\nHello World")

print("hello " + "world " * 3)

print("1. Mix 500g of Flour, 10g Yeast and 300ml Water in a bowl.")
print("2. Knead the dough for 10 minutes.")
print("3. Add 3g of Salt.")
print("4. Leave to rise for 2 hours.")
print("5. Bake at 200 degrees C for 30 minutes.")

username = input("Enter your username: ")
length = len(username)
print(length)

# We have 2 variables glass1 and glass2. glass1 contains milk and glass2 contains juice. Write 3 lines of code to switch the contents of the variables. You are not allowed to type the words "milk" or "juice". You are only allowed to use variables to solve this exercise.

glass1 = "milk"
glass2 = "juice"
glass3 = glass1
glass1 = glass2
glass2 = glass3
print(glass1, glass2)