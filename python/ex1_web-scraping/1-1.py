import requests
from bs4 import BeautifulSoup
import csv
import re   
import time
import ssl
from urllib.parse import urlparse
import pandas as pd

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
    match = re.match(r'([^都道府県]+[都道府県])([^市区町村]+[市区町村])(.+)', address)
    if match:
        return match.groups()
    return "", "", address  # 住所が特殊な場合はそのまま返す        

url = "https://r.gnavi.co.jp/area/tokyo/izakaya/rs/"
response = requests.get(url)
html = response.text
soup = BeautifulSoup(html, "html.parser")

elems = soup.select("#__next > div > div.layout_body__LvaRc > main > div.style_resultRestaurant__WhVwP > div:nth-child(2) > div:nth-child(3) > article > div.style_title___HrjW > a")
#店舗ページへのURLをリストに格納
store_links = [elem.attrs['href'] for elem in elems[:50]]
print(store_links)
data=[]
for store_links in store_links:
    store_res = requests.get(store_links)
    time.sleep(3) #アイドリングタイム
    store_res.encoding = store_res.apparent_encoding #文字化け対策
    store_soup = BeautifulSoup(store_res.text, "html.parser")

    store_name = store_soup.find("p",class_ = "fn org summary",id="info-name").get_text()
    store_phone = store_soup.find("span",class_ = "number").get_text()
    store_mail = ""
    region = store_soup.find("span",class_ = "region").get_text()
    locality = store_soup.find("span",class_ = "locality").get_text()
    prefecture ,city ,street = split_address(region)
    print(store_name, store_phone,prefecture,city,street,locality)    
    store_url = ""
    store_ssl = ""
    data.append([store_name, store_phone, store_mail, prefecture, city, street, locality, store_url, store_ssl])

#CSV出力
df = pd.DataFrame(data,columns=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"])
df.to_csv(r"C:\Users\fu3ka\OneDrive\デスクトップ\Exercise_for_Pool\python\ex1_web-scraping\1-1.csv",encoding="utf-8")