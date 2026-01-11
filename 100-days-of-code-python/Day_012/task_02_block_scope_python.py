game_level = 5  # global scope variable

enemies = ["Goblin", "Troll", "Dragon"]  # global scope variable

if game_level <= 5:
    next_enemy = enemies[0]
# if, while, for blocks do not create a new scope in Python

# Accessible here since next_enemy is defined in the outer scope
print(f"New enemy created: {next_enemy}")


def create_enemy():
    new_enemy = ""
    if game_level >= 3:
        new_enemy = enemies[0]  # block scope within if statement
    print(f"Enemy created inside function: {new_enemy}")

create_enemy()