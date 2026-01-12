
enemies = 1  # global scope variable


def increase_enemies():
    global enemies
    enemies += 1  # Modify the global variable
    print(f"Enemies inside function: {enemies}")


increase_enemies()
print(f"Enemies outside function: {enemies}")
