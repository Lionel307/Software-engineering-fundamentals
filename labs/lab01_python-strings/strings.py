'''
TODO Complete this file by following the instructions in the lab exercise.
'''

strings = ['This', 'list', 'is', 'now', 'all', 'together']
new_sentence = ''
# loops through the list
for word in strings:
    new_sentence += word
    new_sentence += " "
# removes the space at the end
new_sentence = new_sentence.strip()
print(new_sentence)