from multiprocessing import Pool
from bs4 import BeautifulSoup
import requests
from str_n_asin_db import search_word
from str_n_asin_db import asin_db


def connect_to_amazon(URL):
    # connecting to amazon search page. headers help bypass amazon block
    target_web_page = requests.get(URL, headers={"User-Agent": "Defined"})
    if target_web_page.status_code == 200:
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


def compare(list):
    count_seen = 0
    for item in list:
        if item[0] in asin_db:
            count_seen += 1
    return count_seen


def search_db(item):
    URL = "https://www.amazon.com/s/ref=nb_sb_noss_2?url=search-alias%3Daps&field-keywords=" + item
    return URL


def multi_grt(word):
    data_asin_dict = connect_to_amazon(search_db(word))
    count = compare(data_asin_dict)
    return {word: count}


def main():
    good_word = []
    need_to_check_words = []
    bad_words = []
    search_words = search_word()
    p = Pool(2)
    count_list = p.map(multi_grt, search_words)
    for item in count_list:
        for i in item:
            if item[i] == 0:
                bad_words.append(i)
            elif item[i] >= 3:
                good_word.append(i)
            else:
                need_to_check_words.append(i)
    print("good words  :",good_word.__len__(),"\n", good_word,"\n")
    print("bad words  :",bad_words.__len__(),"\n",bad_words,"\n")
    print("need to check words  :",need_to_check_words.__len__(),"\n",need_to_check_words,"\n")


if __name__ == '__main__':
    main()

