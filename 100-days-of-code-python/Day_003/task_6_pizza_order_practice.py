# todo: work out the pizza bill based on the size, pepperoni, and cheese added


print("Welcome to Python Pizza Deliveries!")
size = input("What size pizza do you want? S ($15), M ($20), or L ($25): ")
add_pepperoni = input("Do you want pepperoni? Y ($2 for S, $3 for M/L) or N: ")
extra_cheese = input("Do you want extra cheese? Y ($1) or N: ")

bill = 0

if size == "S":
    bill += 15
    if add_pepperoni == "Y":
        bill += 2
elif size == "M":
    bill += 20
    if add_pepperoni == "Y":
        bill += 3
elif size == "L":
    bill += 25
    if add_pepperoni == "Y":
        bill += 3

if extra_cheese == "Y":
    bill += 1

print(f"Thank you for your order!!! Your final bill is: ${bill}.")

