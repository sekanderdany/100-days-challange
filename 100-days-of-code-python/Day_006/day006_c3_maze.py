
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

def right_is_clear():
    print("Checking if right is clear")
    return False

def turn_right():
    turn_left()
    turn_left()
    turn_left()

while not at_goal():
    if right_is_clear():
        turn_right()
        move()
    elif front_is_clear():
        move()
    else:
        turn_left()