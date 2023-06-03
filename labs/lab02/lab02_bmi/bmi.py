##def bmi():
weight = float(input("What is your weight in kg? "))
height = float(input("What is your height in m? "))
BMI = round(weight/(height*height), 1)
print(f"Your BMI is {BMI}")