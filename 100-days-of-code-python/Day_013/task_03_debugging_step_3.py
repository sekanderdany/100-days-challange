# Step 3 - Play Computer and Evaluate each Line

year = int(input("What's your year of birth? "))

if year > 1980 and year < 1994:
    print("You are a millenial.")
elif year > 1994:
    print("You are a Gen Z.")


'''
- go through your code line by line and write down the value of the relevant variables at each step in the code.

- for example lets say the input is year 1994:
if [year > 1980] = True and [year < 1994] = False: so True + False = False
- So there will be no print output for millenial
elif [year > 1994] also False:
- So there will be no print output for Gen Z 
'''

# Solution

if year > 1980 and year < 1994:
    print("You are a millenial.")
elif year >= 1994: # Correct condition
    print("You are a Gen Z.")
