#!/usr/bin/env python3
import os
import os.path
#from datetime import datetime
#import time
#from multiprocessing.pool import Pool
import json
import requests
from bs4 import BeautifulSoup

#import pandas as pd
#import csv
# from lxml.html import fromstring
#import codecs

# from threading import Thread
from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.keys import Keys
#from selenium.common.exceptions import NoSuchElementException
#from itertools import cycle
from random import randint
import time

#import re

driver = None

def make_root_url(url):
    # com = re.compile('-f-[0-9]+-0-p[0-9].php$')
    # search_list = com.findall(url)
    # if len(search_list) > 0:
    s_ary = url.split('-0-')
    if len(s_ary) > 1:
        return s_ary[0].replace('-f-', '-') + '.php'
    else:
        return url


def get_soup_from_url_by_request(url):
    time.sleep(randint(3, 6))
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
        "Host": "www.gsmarena.com",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }
    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        print('gsmarena request error')
        return False
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        return soup


def get_gsmarena(url):
    page = get_soup_from_url_by_request(url)
    page_urls = [url]

    nav = page.find('div', {'class': 'nav-pages'})
    if nav:
        page_url_list = nav.find_all('a')
        for page_url_a in page_url_list:
            href = page_url_a.get('href')
            page_urls.append('https://www.gsmarena.com/' + href)
        print(page_urls)

    for page_url in page_urls:
        page = get_soup_from_url_by_request(page_url)
        print("page url: ", page_url)
        # get products on one page.
        product_lis = page.find('div', {'class': 'makers'}).find_all('li')
        gsmarena_product_num = 0
        for product in product_lis:
            p_href = product.find('a').get('href')
            print('product url: ', p_href)
            new_product_path = 'output/' + p_href.replace('.php', '.json').replace(' ', '_').replace('(', '').replace(')', '')
            if os.path.isfile(new_product_path):
                print("File exist: ", new_product_path)
                continue
            product = get_product_detail_from_gsmarena('https://www.gsmarena.com/' + p_href)
            if not product:
                continue
            print('gsmarena_product_name: ', product['name'])
            product['GsmarenaCrawled'] = int(time.time())
            product_statistics, category_url_ary = get_product_detail_from_tokopedia(product['name'])
            product['TokopediaCrawled'] = int(time.time())
            if len(product_statistics) == 0 or len(product_statistics['urls']) == 0:
                product['NewMaxPrice'] = 0
                product['NewMinPrice'] = 0
                product['NewMiddlePrice'] = 0
                product['NewAvgPrice'] = 0
                product['SecondhandMaxPrice'] = 0
                product['SecondhandMinPrice'] = 0
                product['SecondhandMiddlePrice'] = 0
                product['SecondhandAvgPrice'] = 0
                product['urls'] = []
                product['firstpagecatstats'] = []
            else:
                product['NewMaxPrice'] = product_statistics['NewMaxPrice']
                product['NewMinPrice'] = product_statistics['NewMinPrice']
                product['NewMiddlePrice'] = product_statistics['NewMiddlePrice']
                product['NewAvgPrice'] = product_statistics['NewAvgPrice']
                product['SecondhandMaxPrice'] = product_statistics['SecondhandMaxPrice']
                product['SecondhandMinPrice'] = product_statistics['SecondhandMinPrice']
                product['SecondhandMiddlePrice'] = product_statistics['SecondhandMiddlePrice']
                product['SecondhandAvgPrice'] = product_statistics['SecondhandAvgPrice']
                product['urls'] = product_statistics['urls']
                product['firstpagecatstats'] = category_url_ary
            with open(new_product_path, 'w') as outfile:
                json.dump(product, outfile)
            gsmarena_product_num = gsmarena_product_num + 1


def get_product_detail_from_gsmarena(product_url):
    product_page = get_soup_from_url_by_request(product_url)
    product = {}
    if product_page.find('h1', {'class': 'specs-phone-name-title'}):
        product['name'] = product_page.find('h1', {'class': 'specs-phone-name-title'}).text
    else:
        return False

    if product_page.find_all('span', {'class': 'specs-brief-accent'}) and len(product_page.find_all('span', {'class': 'specs-brief-accent'})) > 0:
        main_attrs = product_page.find_all('span', {'class': 'specs-brief-accent'})
        for main_attr in main_attrs:
            if main_attr.find('i', {'class': 'head-icon icon-launched'}):
                product['releasedDate'] = main_attr.text.strip()
            if main_attr.find('i', {'class': 'head-icon icon-mobile2'}):
                product['body'] = main_attr.text.strip()
            if main_attr.find('i', {'class': 'head-icon icon-os'}):
                product['os'] = main_attr.text.strip()
            if main_attr.find('i', {'class': 'head-icon icon-sd-card-0'}):
                product['sdCard'] = main_attr.text.strip()

    popularity = product_page.find('li', {'class': 'light pattern help help-popularity'})
    if popularity:
        product['popularity'] = popularity.find('strong').text.strip()
        product['popularityHits'] = popularity.find('span').text.strip()

    fans = product_page.find('li', {'class': 'light pattern help help-fans'})
    if product_page.find('li', {'class': 'light pattern help help-fans'}):
        product['fans'] = fans.find('strong').text.strip()
        product['fansD'] = fans.find('span').text.strip()

    display = product_page.find('li', {'class': 'help accented help-display'})
    if display:
        product['displaySize'] = display.find('strong').text.strip()
        product['displayRes'] = display.find('div').text.strip()

    camera = product_page.find('li', {'class': 'help accented help-camera'})
    if camera:
        product['cameraPixels'] = camera.find('strong').text.strip()
        product['videoPixels'] = camera.find('div').text.strip()

    expansion = product_page.find('li', {'class': 'help accented help-expansion'})
    if expansion:
        product['ramSize'] = expansion.find('strong').text.strip()
        product['chipSet'] = expansion.find('div').text.strip()

    battery = product_page.find('li', {'class': 'help accented help-battery'})
    if battery:
        product['batSize'] = battery.find('strong').text.strip()
        product['batType'] = battery.find('div').text.strip()

    specs_list = product_page.find('div', {'id': 'specs-list'})
    if specs_list:
        versions = specs_list.find('p')
        if versions:
            product['versions'] = str(versions)
        tables = product_page.find_all('table')
        for table in tables:
            if table.get('cellspacing') == None or table.get('cellspacing') != '0':
                continue
            scope_html = table.find('th')
            key = ''
            if scope_html:
                scope = scope_html.text.strip()
                trs = table.find_all('tr')
                for tr in trs:
                    sub_scope_html = tr.find('td', {'class': 'ttl'})
                    if sub_scope_html:
                        sub_scope = sub_scope_html.text.strip()
                        if str(sub_scope_html) != '<td class="ttl"> </td>':
                            key = scope.lower() + sub_scope.capitalize()
                            key = key.replace(' ', '_')
                            product[key] = []
                        elif table.find('td', {'class': 'ttl'}):
                            key = scope.lower()
                            key = key.replace(' ', '_')
                            product[key] = []

                    if key != '':
                        context_html = tr.find('td', {'class': 'nfo'})
                        if context_html:
                            context = context_html.text.strip()
                            product[key].append(context)
    return product


def get_soup_from_driver(driver, url = '', delay_time = 0):
    print(url)
    if url != '':
        driver.get(url)
    if delay_time > 0:
        time.sleep(delay_time)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('div', {'id': 'chrome_desktop_backend'}):
        soup.find('div', {'id': 'chrome_desktop_backend'}).extract()
    return soup


def check_same_name(keystr, comstr):
    f_low_name = comstr.lower()
    f_low_name = f_low_name.replace(')', '').replace('(', '')
    f_low_name_ary = f_low_name.split()
    product_low_name = keystr.lower()
    product_low_name = product_low_name.replace(')', '').replace('(', '')
    product_low_name_ary = product_low_name.split()

    for p in product_low_name_ary:
        if not p in f_low_name_ary:
            print(f'first_product_name "{comstr}" != product_name "{keystr}"')
            return False
    print(comstr)
    return True


def get_product_detail_from_tokopedia(product_name):
    url = 'https://www.tokopedia.com'
    driver.get(url)
    soup = get_soup_from_driver(driver, '', 1)
    if soup.find('div', {'id': 'chrome_desktop_backend'}):
        soup.find('div', {'id': 'chrome_desktop_backend'}).extract()
    input_keyword_class = 'css-1w2ezbs e16vycsw0'
    if not soup.find('input', {'class': input_keyword_class}):
        soup = get_soup_from_driver(driver, '', 2)
        if not soup.find('input', {'class': input_keyword_class}):
            soup = get_soup_from_driver(driver, '', 3)
            if not soup.find('input', {'class': input_keyword_class}):
                return [], None
    driver.find_element_by_xpath("//input[@class='" + input_keyword_class + "']").send_keys(product_name)
    button_class = 'css-9gksxa e1v0ehno1'
    if not soup.find('button', {'class': button_class}):
        soup = get_soup_from_driver(driver, '', 1)
        if not soup.find('button', {'class': button_class}):
            soup = get_soup_from_driver(driver, '', 2)
            if not soup.find('button', {'class': button_class}):
                return [], None
    driver.find_element_by_xpath("//button[@class='" + button_class + "']").click()
    time.sleep(2)
    html = driver.page_source
    search_soup = BeautifulSoup(html, 'html.parser')
    search_content = search_soup.find('div', {'class': 'css-jza1fo'})
    if search_content:
        first_products = search_content.find_all('div', {'class': 'css-1g20a2m'})
        if len(first_products) == 0:
            return [], None
        category_url_list = []
        category_url_count = []
        category_url_ary = []
        first_product_num = 0
        for first_product in first_products:
            first_product_num = first_product_num + 1
            print(first_product_num)

            a_tag = first_product.find('a')
            if a_tag:
                first_product_name = first_product.find('span', {'class': 'css-1bjwylw'}).text.strip()
                if not check_same_name(product_name, first_product_name):
                    continue
                url = a_tag.get('href')
                product_page = get_soup_from_driver(driver, url)
                category_class = 'css-1ylo27j'
                category_header = product_page.find('ol', {'class': category_class})
                if category_header == None:
                    product_page = get_soup_from_driver(driver, '', 1)
                    category_header = product_page.find('ol', {'class': category_class})
                    if category_header == None:
                        product_page = get_soup_from_driver(driver, '', 2)
                        category_header = product_page.find('ol', {'class': category_class})
                        if category_header == None:
                            product_page = get_soup_from_driver(driver, '', 3)
                            category_header = product_page.find('ol', {'class': category_class})
                            if category_header == None:
                                continue
                category_list = category_header.find_all('li')
                category_len = len(category_list)
                print('category len: ', category_len)
                if category_len < 2:
                    continue
                main_category = category_list[category_len - 2]
                category_a_tag = main_category.find('a')
                if category_a_tag:
                    category_url = category_a_tag.get('href')
                    print('category_url: ', category_url)
                    # ignore accessories, earphone, produk-lainnya
                    if 'aksesoris' in category_url:
                        print('ignoring aksesoris')
                        continue
                    if 'earphone' in category_url:
                        print('ignoring earphone')
                        continue
                    if 'produk-lainnya' in category_url:
                        print('ignoring produk-lainnya')
                        continue
                    if category_url in category_url_list:
                        index = category_url_list.index(category_url)
                        category_url_count[index] = category_url_count[index] + 1
                        category_url_ary[index]['count'] = category_url_count[index]
                        # if category_url_count[index] == 40:
                        #     return get_from_max_category(product_name, category_url)
                    else:
                        category_url_list.append(category_url)
                        category_url_count.append(1)
                        category_url_ary.append({'count': 1, 'url': category_url})
        print(category_url_count)
        if len(category_url_count) == 0:
            return [], None
        max_count = max(category_url_count)
        max_index = category_url_count.index(max_count)
        max_category_url = category_url_list[max_index]
        return get_from_max_category(product_name, max_category_url), category_url_ary
    else:
        return [], None


def get_from_max_category(product_name, max_url):
    url_ary = []
    product_num = 0
    condition = 1
    product_statistics = {
        'NewMaxPrice': 0,
        'NewMinPrice': 0,
        'NewMiddlePrice': 0,
        'NewAvgPrice': 0,
        'SecondhandMaxPrice': 0,
        'SecondhandMinPrice': 0,
        'SecondhandMiddlePrice': 0,
        'SecondhandAvgPrice': 0,
        'urls': []
    }
    while condition < 3:
        price_ary = []
        page_num = 1
        while True:
            print('urls len: ', len(url_ary))
            url = max_url + '?page=' + str(page_num) + '&condition=' + str(condition)
            max_category_soup = get_soup_from_driver(driver, url)

            pagination_class = 'css-uoymjt-unf-pagination'
            if not max_category_soup.find('div', {'class': pagination_class}):
                max_category_soup = get_soup_from_driver(driver, '', 1)
                if not max_category_soup.find('div', {'class': pagination_class}):
                    max_category_soup = get_soup_from_driver(driver, '', 1)
                    if not max_category_soup.find('div', {'class': pagination_class}):
                        max_category_soup = get_soup_from_driver(driver, '', 3)
                        if not max_category_soup.find('div', {'class': pagination_class}):
                            print("not max_category_soup.find('div', {'class': pagination_class})")
                            break
            print('page_num: ', page_num)
            page_num = page_num + 1

            #products_box = max_category_soup.find('div', {'class': 'css-13l3l78 e1nlzfl13'})
            products_box = max_category_soup.find('div', {'class': 'css-886sl6 exx5nxl3'})
            if not products_box:
                print('not products_box')
                break
            
            #products = products_box.find_all('div', {'class': 'css-bk6tzz e1nlzfl3'})
            products = products_box.find_all('div', {'class': 'css-bk6tzz exx5nxl2'})
            if len(products) == 0:
                print('len(products) == 0')
                break

            for product in products:
                product_name_html = product.find('span', {'class': 'css-1bjwylw'})
                if not product_name_html:
                    print('not product_name_html')
                    continue
                name = product_name_html.text.strip()
                if not check_same_name(product_name, name):
                    continue

                product_a_tag = product.find('a', {'class': 'css-89jnbj'})
                if not product_a_tag:
                    print('not product_a_tag')
                    continue
                product_url = product_a_tag.get('href')
                price_html = product.find('span', {'class': 'css-o5uqvq'})
                if price_html:
                    price = price_html.text.strip()
                    price = price.replace('Rp', '')
                    price = price.replace('.', '')
                    price = int(price)
                else:
                    print('not price_html')
                    continue
                product_num = product_num + 1
                print('product_num: ', product_num)
                if condition == 1:
                    url_ary.append([product_url, name, price, 'New'])
                else:
                    url_ary.append([product_url, name, price, 'Secondhand'])
                price_ary.append(price)
        if len(price_ary) > 0 and condition == 1:
            product_statistics['NewMaxPrice'] = max(price_ary)
            product_statistics['NewMinPrice'] = min(price_ary)
            product_statistics['NewAvgPrice'] = sum(price_ary) / len(price_ary)
            product_statistics['NewMiddlePrice'] = (max(price_ary) + min(price_ary)) / 2
        if len(price_ary) > 0 and condition == 2:
            product_statistics['SecondhandMaxPrice'] = max(price_ary)
            product_statistics['SecondhandMinPrice'] = min(price_ary)
            product_statistics['SecondhandAvgPrice'] = sum(price_ary) / len(price_ary)
            product_statistics['SecondhandMiddlePrice'] = (max(price_ary) + min(price_ary)) / 2
        condition = condition + 1
    product_statistics['urls'] = url_ary
    return product_statistics

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('window-position=0,0')
    options.add_argument('window-size=1200x700')
    driver = webdriver.Chrome(options=options)
    # url = input('please input gsmarena url: ')
    #url = 'https://www.gsmarena.com/samsung-phones-9.php'
    #url = 'https://www.gsmarena.com/google-phones-107.php'
    #url = 'https://www.gsmarena.com/oneplus-phones-95.php'
    #url = 'https://www.gsmarena.com/xiaomi-phones-80.php'
    #url = 'https://www.gsmarena.com/oppo-phones-f-82-0-r1-p1.php'
    #url = 'https://www.gsmarena.com/apple-phones-48.php'
    #url = make_root_url(url)
    #get_gsmarena(url)
    #out, out2 = get_from_max_category('Apple Watch Series 3','https://www.tokopedia.com/p/handphone-tablet/wearable-devices/smart-watch')
    # print(out)
    print('Done')

