

# asks the user to think of a number between 1-100
print("Pick a number between 1 and 100 (inclusive)")
guess_answer = 50
upper_bound = 100
lower_bound = 1


# if the guess is too high, change the lower_bound
def higher(answer):
    global lower_bound 
    lower_bound = answer
    global guess_answer 
    guess_answer = int((upper_bound + lower_bound)/2)
# if the guess is too low, change the higher_bound
def lower(answer):
    global upper_bound 
    upper_bound = answer
    global guess_answer 
    guess_answer = int((upper_bound + lower_bound)/2)

correct = False
while correct is False:
    print(f"My guess is: {guess_answer}")
    print("Is my guess too low (L), too high (H), or correct (C)?")
    real_answer = input()
    if real_answer is "L":
        higher(guess_answer)
    elif real_answer is "H":
        lower(guess_answer)
    elif real_answer is "C":
        correct = True
print("Got it!")



    
