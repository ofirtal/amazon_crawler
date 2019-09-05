import csv

asin_db = ['B0002LCUZK', 'B000RMU6S2', 'B06Y1NKBJ3',
           'B00JIX4ORA', 'B00JIX54RY', 'B000RMU6S2',
           'B01B25NN64', 'B07M7JQ1VY', 'B07GB2KLYY',
           'B07CN22C56', 'B075F1N2DM', 'B01B254OVC']


def search_word():
    search_strings = csv.reader(open('search_words.csv'))
    search_words = []
    for row in search_strings:
        new = row[0]
        ready = new.replace(" ", "+")
        search_words.append(ready)
    search_words.pop(0)
    return search_words
