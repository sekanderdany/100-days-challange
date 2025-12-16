friends = ["Alice", "Bob", "Charlie", "David"]

def who_pays_bill(friends_list):
    import random
    payer = random.choice(friends_list)
    return payer

bill_payer = who_pays_bill(friends)
print(f"{bill_payer} is going to pay the bill today!")