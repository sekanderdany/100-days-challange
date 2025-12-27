def greet_with(name= "Dany", location="Germany", time="morning"):
    print(f"Hello {name}!")
    print(f"Good {time}!")
    print(f"What is it like in {location}?")
    
greet_with("Dany", "Germany", "morning")
greet_with(time="afternoon", location="Italy", name="Alice")