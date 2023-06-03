income = float(input("Enter your income: "))
if income <= 18200:
    print("The estimated tax on your income is $0")
elif income >= 18201 and income <= 37000:
    amount = round((income - 18200)*0.19, 2) 
    # changes to the format as currency
    tax = "${:,.2f}".format(amount)
    print(f"The estimated tax on your income is {tax}")

elif income >= 37001 and income <= 87000:
    amount = round((income - 37000)*0.325, 2) + 3572
    # changes to the format as currency
    tax = "${:,.2f}".format(amount)

    print(f"The estimated tax on your income is {tax}")
elif income >= 87001 and income <= 180000:
    amount = round((income - 87000)*0.37, 2) + 19822
    # changes to the format as currency
    tax = "${:,.2f}".format(amount)

    print(f"The estimated tax on your income is {tax}")
elif income >= 180001:
    amount = round((income - 180000)*0.45, 2) + 54232
    # changes to the format as currency
    tax = "${:,.2f}".format(amount)
    print(f"The estimated tax on your income is ${tax}")