#!/usr/bin/env python3

from selenium import webdriver
import unicodedata
import re
import os
import time
from bs4 import BeautifulSoup
import random
import json
import csv

def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


driver = None

# load database
productdb = {}
with open('productdb.json', 'r') as f:
    lines = f.readlines()
    productdb = json.loads("\n".join(lines))

CACHE_DIR = './cache/'

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

def skip(url):
    if url is None:
        return True
    if '/discovery' in url:
        return True
    if '/blog/' in url:
        return True
    if '/about' in url:
        return True
    if '/privacy' in url:
        return True
    if '/cod' in url:
        return True
    if '/daftar-halaman' in url:
        return True
    if '/find' in url:
        return True
    if '/terms' in url:
        return True
    if '/pinjaman-online' in url:
        return True
    if '/help' in url:
        return True
    if '/careers' in url:
        return True
    if '/partner' in url:
        return True
    if '/mitra-toppers' in url:
        return True
    if '/intellectual-property-protection' in url:
        return True
    return False

def crawl(url):
    if skip(url):
        return
    
    fname = slugify(url)
    fpath = CACHE_DIR + fname + '.html'
    html = ''
    if os.path.exists(fpath):  # load from cache
        with open(fpath) as f:
            lines = f.readlines()
            html = "\n".join(lines)

    else:  # crawl and save to cache
        driver.get(url)
        time.sleep(1+random.random() * 2)
        html = driver.page_source
        with open(fpath, 'w') as f:
            f.write(html)

    # create parser
    soup = BeautifulSoup(html, 'html.parser')
    if soup.find('div', {'id': 'chrome_desktop_backend'}):
        soup.find('div', {'id': 'chrome_desktop_backend'}).extract()

    if 'p/handphone-tablet/' in url:  # main page
        anchors = soup.find_all('a')
        random.shuffle(anchors)
        for a in anchors:
            href = a.get('href')
            if href is None:
                continue
            if href.startswith('https://www.tokopedia.com/'):
                crawl(href)
    elif fpath not in productdb:  # product page
        h1 = soup.find('h1')
        price = soup.find('div', {'class': 'price'})
        rating = soup.find('span', {'data-testid': 'lblPDPDetailProductRatingNumber'})
        img = soup.find('div', {'id': 'pdp_comp-product_media'})
        if img is None:
            img = ''
        else:
            img = img.find('img')
            if img is None:
                img = ''
            else:
                img = img.attrs['src']
        desc = soup.find('div', {'role': 'tabpanel'})
        merchant = soup.find('h2')
        if h1 is None or desc is None or price is None or rating is None or merchant is None:
            print(f'h1={h1},desc={desc},price={price},rating={rating},merchant={merchant} one of them is none')
            return
        productdb[fpath] = {
            # 1. Name of Product
            'title': h1.text,
            # 2. Description
            'desc': desc.text,
            # 3. Image Link
            'image': img,
            # 4. Price
            'price': price.text,
            # 5. Rating (out of 5 stars)
            'rating': rating.text,
            # 6. Name of store or merchant
            'merchant': merchant.text,
        }
        with open('productdb.json', 'w') as f:
            json.dump(productdb, f, indent=2, sort_keys=True)


if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}  # ,"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    options.add_argument('window-position=0,0')
    options.add_argument('window-size=1200x720')
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(options=options)
    urls = [
        'https://www.tokopedia.com/p/handphone-tablet/handphone',
        'https://www.tokopedia.com/p/handphone-tablet/handphone?page=2', # until this only 89 items properly parsed
        'https://www.tokopedia.com/p/handphone-tablet/handphone?page=3'
    ]
    for url in urls:
        crawl(url)
    with open('productsdb.csv','w') as f:
        w = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        count = 0
        w.writerow(['title','desc','image','price','rating','merchant'])
        for kv in productdb.items():
            row = kv[1]
            w.writerow([row['title'],row['desc'],row['image'],row['price'],row['rating'],row['merchant']])
            count += 1
            if count >= 100:
                break
    print('Done')
