import requests
from bs4 import BeautifulSoup
import csv
import re   
import time
import ssl
from urllib.parse import urlparse
import pandas as pd
from urllib.parse import urljoin

#ユーザーエージェントの設定
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
header = {
    'User-Agent': user_agent
}


#住所の分割処理
def split_address(address):
    match = re.match( r'(.+?[都道府県])(.+?[市区町村])?(.*)', address)
    if match:
        return match.groups()
    return "", "", address  # 住所が特殊な場合はそのまま返す        

url = "https://r.gnavi.co.jp/area/tokyo/izakaya/rs/"
response = requests.get(url,headers=header)
html = response.text
soup = BeautifulSoup(html, "html.parser")

store_links = []
for i in range(1,3):
    # 1ページ目はそのままのURL
    if i==1:
        page_url=url
    else:
    # 2ページ以降はURLをつなげる
        page_url=urljoin(url,'?p={i}')
    # 1～3ページのそれぞれのURLにアクセス
    response = requests.get(url,headers=header)
    
    html = response.text
    soup = BeautifulSoup(html, "html.parser")   
    elems=soup.find_all(href=re.compile("gnavi.co.jp"),class_ = "style_titleLink__oiHVJ")

    #各店舗ページへのURLリスト取得
    for elem in elems:
        if "PREF" not in elem.attrs['href']: #PRを除外
            store_links.append(elem.attrs['href'])
    time.sleep(3) #アイドリングタイム

    

data=[]

#各店舗情報を取得
for store_link in store_links[:50]:
    store_res = requests.get(store_link,headers=header)
    time.sleep(3) #アイドリングタイム
    store_res.encoding = store_res.apparent_encoding #文字化け対策
    store_soup = BeautifulSoup(store_res.text, "html.parser")

    store_name = store_soup.find("p",class_ = "fn org summary",id="info-name").get_text()
    store_phone = store_soup.find("span",class_ = "number").get_text()

    mail_element = store_soup.find(href=re.compile("mailto:"))
    #メールがない場合、空文字を入れる
    if mail_element:
        store_mail = mail_element["href"].replace("mailto:", "")
    else:
        store_mail = ""

    region = store_soup.find("span",class_ = "region").get_text()
    prefecture ,city ,street = split_address(region)

    locality = store_soup.find("span",class_ = "locality")
    #建物名がない場合、空文字を入れる
    if locality:
        locality = locality.get_text()
    else:
        locality = ""
    
       
    store_url = ""
    store_ssl = ""
    data.append([store_name, store_phone, store_mail, prefecture, city, street, locality, store_url, store_ssl])

#CSV出力
df = pd.DataFrame(data,columns=["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"])
df.to_csv(r"C:\Users\fu3ka\OneDrive\デスクトップ\Exercise_for_Pool\python\ex1_web-scraping\1-1.csv", index = False, encoding="utf-8-sig")