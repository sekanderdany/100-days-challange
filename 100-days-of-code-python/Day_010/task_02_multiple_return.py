f_name = input("Enter your first name: ").strip()
l_name = input("Enter your last name: ").strip()

def format_name(f_name, l_name):
    if f_name == "" or l_name == "":
        return "You didn't provide valid inputs."
    else:
        f_name = f_name.title()
        l_name = l_name.title()
        return f"{f_name} {l_name}"

formatted_name = format_name(f_name, l_name)
print(f"Formatted Name: {formatted_name}")