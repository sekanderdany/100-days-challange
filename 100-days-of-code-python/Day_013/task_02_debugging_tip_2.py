# Step 2 - Reproduce the bug

from random import randint
dice_images = ["❶", "❷", "❸", "❹", "❺", "❻"]
dice_num = randint(1, 6)
# print(dice_images[dice_num])

'''
Some bugs are sneaky, they only occur under certain conditions. In order to debug them, we need to be able to reliably reproduce the bug and diagnose our problem to figure out which conditions trigger the bug.

# 1. Change the code so that it always produces the occasional error.
# 2. Fix the code and remove the bug.

'''
# 1. Reproduce the bug

# dice_num = 1
# dice_num = 2
# dice_num = 3
# dice_num = 4
# dice_num = 5
dice_num = 6 # Found it

# print(dice_images[dice_num])

# 2. Fixed Code


dice_num = randint(0, 5)
print(dice_images[dice_num])
