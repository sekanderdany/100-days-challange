capitals = {
    'France': 'Paris',
    'Germany': 'Berlin',
}

# Nested List in a Dictionary

travel_log = {
    "France": ["Paris", "Lyon", "Nice"],
    "Germany": ["Berlin", "Munich", "Hamburg"],
}

print(travel_log["France"][1])  # Output: Lyon

nested_list = ["A", "B", ["C", "D", "E"], "F"]

print(nested_list[2][1])  # Output: D

another_travel_log = {
    "France": {
        "num_times_visited": 12,
        "cities_visited": ["Paris", "Lyon", "Nice"],
    },
    "Germany": {
        "num_times_visited": 5,
        "cities_visited": ["Berlin", "Munich", "Hamburg"],
    },
}

print(another_travel_log["Germany"]["cities_visited"][2])  


order = {
    "starter": {1: "Salad", 2: "Soup"},
    "main": {1: ["Burger", "Fries"], 2: ["Steak"], 4: ["Pasta"]},
    "dessert": {1: ["Ice Cream"], 2: []},
}

print(order["main"][4][0])  # Output: Pasta