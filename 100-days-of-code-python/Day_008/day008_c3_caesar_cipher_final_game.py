# Caesar Cipher

from day008_c3_art import logo

print(logo)

alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

def caesar(original_text, shift_amount, encode_or_decode):
    output_text = ""
    if encode_or_decode == "decode":
         shift_amount *= -1
    for letter in original_text:
        if letter not in alphabet:
            output_text += letter
        else :
            shifted_position = alphabet.index(letter) + shift_amount
            shifted_position %= len(alphabet)
            output_text += alphabet[shifted_position]

    print(f"The {encode_or_decode}d text is {output_text}")

should_continue = True
while should_continue:
    direction = input("Type 'encode' to encrypt, type 'decode' to decrypt:\n")
    text = input("Type your message:\n").lower()
    shift = int(input("Type the shift number:\n"))

    caesar(original_text=text, shift_amount=shift, encode_or_decode=direction)
    if input("Type 'yes' if you want to go again. Otherwise type 'no'.\n").lower() == "no":
        should_continue = False
        print("Goodbye!")

'''
def encrypt(plain_text, shift_amount):
    cipher_text = ""
    for letter in plain_text:
        position = alphabet.index(letter)
        new_position = position + shift_amount
        if new_position > 25:
            new_position -= 26
        cipher_text += alphabet[new_position]
    print(f"The encoded text is {cipher_text}")

def decrypt(cipher_text, shift_amount):
    plain_text = ""
    for letter in cipher_text:
        position = alphabet.index(letter)
        new_position = position - shift_amount
        plain_text += alphabet[new_position]
    print(f"The decoded text is {plain_text}")

keep_going = True
while keep_going:
    if direction == "decode":
        decrypt(cipher_text=text, shift_amount=shift)
    elif direction == "encode":
        encrypt(plain_text=text, shift_amount=shift)
    else:
        print("Invalid option! Please choose 'encode' or 'decode'.")

    if input("Type 'yes' if you want to go again. Otherwise type 'no'.\n").lower() == "no":
        keep_going = False
        print("Goodbye!")

'''