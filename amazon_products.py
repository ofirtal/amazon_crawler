# A scraper designed to search amazon for search terms (from a .csv file) and scrape
# the ASIN numbers of the products that appear in the search results.
# The code then compares the ASIN numbers to a target list and categorizes the search terms
# into three categories: Good(returns more than 3 target ASIN numbers),
# Needs further check (1-3) and Bad (0).
# results are returned in the form of a .txt file.


from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests
import time
from str_n_asin_db import search_word
from str_n_asin_db import asin_db


# in: item from list, returning: the url
def search_db(item):
    URL = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + item
    return URL


# in: the url, returning: relevant data_asin_list (after status 200 check)
def connect_to_amazon(URL):
    # connecting to amazon search page.
    target_web_page = requests.get(URL, headers={"User-Agent": "Defined"})
    try:
        target_web_page.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print("Error: " + str(e))
        exit()

    # if target_web_page.status_code == 200:
    soup = BeautifulSoup(target_web_page.content, 'html.parser')
    data_asin_list = []
    results = soup.find_all('div', {'class': "s-result-list s-search-results sg-row"})
    count = 0
    returned_products_from_page = 19
    for link in results:
        for div in link:
            if div is None or div == "\n":
                continue
            if count > returned_products_from_page:
                break
            elif div.get('data-asin') is not None and div.get('data-asin') != "":
                data_asin_list.append([div.get('data-asin'), div.get('data-index')])
                count += 1

    return data_asin_list


# in: data_asin_list, out: number of target data asin in the data asin product list
def num_of_occurances_in_list(data_asin_list):
    count_seen = 0
    for item in data_asin_list:
        if item[0] in asin_db:
            count_seen += 1
    return count_seen


# pairing word with count
def phrase_and_target_asin_count_dict(word):
    data_asin_dict = connect_to_amazon(search_db(word))
    count = num_of_occurances_in_list(data_asin_dict)
    return {word: count}


# generates a txt file with the full data
def generate_txt_file(good_words_list, check_words_list, bad_words_list):
    timestr = time.strftime("%d%m%Y-%H%M%S")
    with open("amazon_{}.txt".format(timestr), "w") as f:
        f.write("Good words: ")
        txt_file_body(good_words_list, f)
        f.write("\n")
        f.write("Need to check: ")
        txt_file_body(check_words_list, f)
        f.write("\n")
        f.write("Bad words: ")
        txt_file_body(bad_words_list, f)


def txt_file_body(list_item, f):
    f.write(str(len(list_item)))
    f.write("\n")
    for i in list_item:
        f.write(i)
        f.write("\n")


def main():
    # output lists
    good_word = []
    need_to_check_words = []
    bad_words = []

    # search_words : list of search terms from csv
    search_words = search_word()

    pool_assign = Pool()
    count_list = pool_assign.map(phrase_and_target_asin_count_dict, search_words)
    good_word_min = 3
    for item in count_list:
        for i in item:
            if item[i] == 0:
                bad_words.append(i)
            elif item[i] >= good_word_min:
                good_word.append(i)
            else:
                need_to_check_words.append(i)
    pool_assign.close()
    pool_assign.join()

    generate_txt_file(good_word, need_to_check_words, bad_words)
    print("good words  :", len(good_word), "\n", good_word, "\n")
    print("need to check words  :", len(need_to_check_words), "\n", need_to_check_words,"\n")
    print("bad words  :", len(bad_words), "\n", bad_words, "\n")


if __name__ == '__main__':
    main()

