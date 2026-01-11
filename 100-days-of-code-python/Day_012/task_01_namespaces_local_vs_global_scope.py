# global scope example
enemies = 1


def increase_enemies():
    enemies = 2
    print(f"Enemies inside function: {enemies}")


increase_enemies()
print(f"Enemies outside function: {enemies}")

# local scope example


def drink_potion():
    potion_strength = 2
    print(f"Potion strength inside function: {potion_strength}")


drink_potion()
# print(f"Potion strength outside function: {potion_strength}")  # This will raise an error


def game():
    level = 3

    def create_enemy():
        enemy_level = level + 1
        print(f"Enemy level inside nested function: {enemy_level}")
    create_enemy()

    # print(f"Enemy level outside nested function: {enemy_level}")  # This will raise an error
game()
