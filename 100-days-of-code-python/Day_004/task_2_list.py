states_of_america = [ "Delaware", "Pennsylvania", "New Jersey", "Georgia", "Connecticut",
                      "Massachusetts", "Maryland", "South Carolina", "New Hampshire",
                        "Virginia", "New York", "North Carolina", "Rhode Island"]

print(states_of_america[-1])
print(states_of_america[0:3])  # Prints the first three states in the list
print(states_of_america[4:8])  # Prints states from index 4 to

states_of_america[1] = "Pencilvania"  # Correcting the spelling of Pennsylvania 7
print(states_of_america)

states_of_america.append("Puerto Rico")  # Adding Puerto Rico to the end of the list 8
print(states_of_america)

states_of_america.extend(["Washington D.C.", "U.S. Virgin Islands"])  # Adding multiple items to the list 9
print(states_of_america)
print(len(states_of_america))  # Prints the total number of states in the list 10