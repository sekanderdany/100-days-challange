# Hurdle 3
# Mock functions for testing
def turn_left():
    print("Turning left")

def move():
    print("Moving forward")

def at_goal():
    print("Checking if at goal")
    return False

def front_is_clear():
    print("Checking if front is clear")
    return True

def wall_in_front():
    print("Checking if wall in front")
    return False

def wall_on_right():
    print("Checking if wall on right")
    return False

def turn_right():
    turn_left()
    turn_left()
    turn_left()

while not at_goal():
    if front_is_clear():
        move()
    elif wall_in_front():
        turn_left()
        move()
        turn_right()
        move()
        turn_right()
        move()
        turn_left()
        

# Hurdle 4

def turn_right():
    turn_left()
    turn_left()
    turn_left()

def jump():
    turn_left()
    while wall_on_right():
        move()
    turn_right()
    move()
    turn_right()
    while front_is_clear():
        move()
    turn_left()

while not at_goal():
    if wall_in_front():
        jump()
    else:
        move()