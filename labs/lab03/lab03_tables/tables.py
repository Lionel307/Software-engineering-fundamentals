import random
"""
The program picks two random integers between 2 and 12, 
and then asks the user to multiply them together in their head 
and then enter their answer.
"""

num_1 = random.randint(2,12)
num_2 = random.randint(2,12)
correct = False
while correct is False:
    answer = int(input(f"What is {num_1} x {num_2}? "))
    if answer == (num_1 * num_2):
        print("Correct!")
        correct = True
    else:
        print("Incorrect - try again.")
