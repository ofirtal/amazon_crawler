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

    # if target_web_page.status_code == 200:
    soup = BeautifulSoup(target_web_page.content, 'html.parser')
    data_asin_list = []
    results = soup.find_all('div', {'class': "s-result-list s-search-results sg-row"})
    count = 0
    for link in results:
        for div in link:
            if div is None or div == "\n":
                continue
            if count > 19:
                break
            elif div.get('data-asin') is not None and div.get('data-asin') != "":
                data_asin_list.append([div.get('data-asin'), div.get('data-index')])
                count += 1

    return data_asin_list


# in: data_asin_list, out: number of target data asin in the data asin product list
def compare(list):
    count_seen = 0
    for item in list:
        if item[0] in asin_db:
            count_seen += 1
    return count_seen


# pairing word with count
def multi_grt(word):
    data_asin_dict = connect_to_amazon(search_db(word))
    count = compare(data_asin_dict)
    return {word: count}


def generate_txt_file(good_words_list, check_words_list):
    timestr = time.strftime("%d%m%Y-%H%M%S")
    with open("amazon_{}.txt".format(timestr), "w") as f:
        f.write("good words: ")
        f.write(str(len(good_words_list)))
        f.write("\n")
        for i in good_words_list:
            f.write(i)
            f.write("\n")
        f.write("need to check: ")
        f.write(str(len(check_words_list)))
        f.write("\n\n\n")
        for i in check_words_list:
            f.write(i)
            f.write("\n")


def main():
    # output lists
    good_word = []
    need_to_check_words = []
    bad_words = []

    # search_words : list of search terms from csv
    search_words = search_word()

    p = Pool()
    count_list = p.map(multi_grt, search_words)
    for item in count_list:
        for i in item:
            if item[i] == 0:
                bad_words.append(i)
            elif item[i] >= 3:
                good_word.append(i)
            else:
                need_to_check_words.append(i)
    p.close()
    p.join()

    generate_txt_file(good_word, need_to_check_words)
    print("good words  :", len(good_word), "\n", good_word, "\n")
    print("need to check words  :", len(need_to_check_words), "\n", need_to_check_words,"\n")
    print("bad words  :", len(bad_words), "\n", bad_words, "\n")

if __name__ == '__main__':
    main()

