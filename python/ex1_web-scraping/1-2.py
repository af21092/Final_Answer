import requests
import csv
import re   
import time
import ssl
from urllib.parse import urlparse

from selenium import webdriver


import chromedriver_binary_sync
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

options = webdriver.ChromeOptions()
options.add_argument('--headless')
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')
pf_path = r"C:\Users\fu3ka\AppData\Local\Google\Chrome\User Data\Default"
options.add_argument(f'user-data-dir={pf_path}')
driver = webdriver.Chrome(options=options)

driver.get("https://r.gnavi.co.jp/area/tokyo/izakaya/rs/")

elems = driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
# store_links = [elem.get_attribute("href") for elem in elems]
store_links = []
for elem in elems:
    if "PREF" not in elem.get_attribute('href'): #PRを除外
            store_links.append(elem.get_attribute('href'))
print(store_links)

#デジタル証明書確認
def ssl_check(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme == "https":
            return True
        else:
            return False
    except:
        return False

#住所の分割処理
def split_address(address):
    match = re.match( r'(.+?[都道府県])(.+?[市区町村])?(.*)', address)
    if match:
        return match.groups()
    return "", "", address  # 住所が特殊な場合はそのまま返す  

# for i in range(1,4):
#     # 1ページ目はそのままのURL
#     if i==1:
#         driver.get("https://r.gnavi.co.jp/area/tokyo/izakaya/rs/")
#     else:
#     # 2ページ以降はURLをつなげる
#         page_url=driver.find_element(By.XPATH,'//*[@id="__next"]/div/div[2]/main/div[11]/nav/ul/li[10]/a').get_attribute('href')
#         driver.get(page_url)
#         print(page_url)
    
#     # 1～3ページのそれぞれのURLにアクセス
#     elems = driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
#     store_links = []
#     for elem in elems:
#         if "PREF" not in elem.get_attribute('href'): #PRを除外
#                 store_links.append(elem.get_attribute('href'))
#         time.sleep(3) #アイドリングタイム

# print(store_links)
# print(len(store_links))

#各店舗情報を取得
data=[]
for store_link in store_links[:1]:
    store_res = driver.get(store_link)
    time.sleep(3) #アイドリングタイム

    store_name = driver.find_element(By.ID, "info-name").text
    store_phone = driver.find_element(By.CLASS_NAME, "number").text

    #メールがない場合があるため、空文字を入れる
    try:
        store_mail = driver.find_element(By.CSS_SELECTOR, ".mail").text
    except NoSuchElementException:
        store_mail = ""  

    region = driver.find_element(By.CLASS_NAME, "region").text
    
    #建物名がない場合があるため、空文字を入れる
    try:
        locality = driver.find_element(By.CLASS_NAME, "locality").text
    except NoSuchElementException:
        locality = ""
    
    prefecture ,city ,street = split_address(region)
    # print(store_name, store_phone,prefecture,city,street,locality)    
    store_url = driver.find_element(By.XPATH, '//*[@id="sv-site"]/li/a').get_attribute("href")
    store_ssl = ssl_check(store_url)
    data.append([store_name, store_phone,  prefecture, city, street, locality, store_url, store_ssl])
print(data)

# CSV出力
f = open(r"C:\Users\fu3ka\OneDrive\デスクトップ\Exercise_for_Pool\python\ex1_web-scraping\1-2.csv", mode = 'w', encoding='utf-8-sig', errors='ignore')

writer = csv.writer(f, lineterminator='\n') 
csv_header = ["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"]
writer.writerow(csv_header)
writer.writerows(data)

f.close()


driver.close()