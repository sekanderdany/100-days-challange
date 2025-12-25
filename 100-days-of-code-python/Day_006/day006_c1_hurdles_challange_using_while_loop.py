# https://reeborg.ca/reeborg.html?lang=en&mode=python&menu=worlds%2Fmenus%2Freeborg_intro_en.json&name=Hurdle%204&url=worlds%2Ftutorial_en%2Fhurdle4.json

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

def jump():
    turn_left()
    move()
    turn_right()
    move()
    turn_right()
    move()
    turn_left()

while not at_goal():
    if wall_in_front():
        jump()
    else:
        move()