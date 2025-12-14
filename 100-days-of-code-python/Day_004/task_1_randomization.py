import random

random_integer = random.randint(a=1, b=10)  # Generates a random integer between 1 and 10 (inclusive)

print(random_integer)

random_number_0_to_1 = random.random() * 10 # Generates a random float between 0.0 and 1.0

print(random_number_0_to_1)

random_float_in_range = random.uniform(a=1, b=10)  # Generates a random float between 1.0 and 10.0

print(random_float_in_range)

random_choice = random.choice(['apple', 'banana', 'cherry', 'date'])  # Randomly selects an item from the list

print(random_choice)

random_sample = random.sample(range(1, 21), 5)  # Randomly selects 5 unique numbers from 1 to 20

print(random_sample)

random_heads_or_tails = random.randint(0, 1)  # Simulates a coin flip (0 for heads, 1 for tails)
if random_heads_or_tails == 0:
    print("Heads")
else:
    print("Tails")