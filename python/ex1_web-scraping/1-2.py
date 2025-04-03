import requests
import csv
import re   
import time
import ssl
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver


import chromedriver_binary_sync
from selenium import webdriver
chrome_driver_path = r"C:\Users\fu3ka\OneDrive\デスクトップ\Exercise_for_Pool\python\ex1_web-scraping\chromedriver.exe"
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

options = webdriver.ChromeOptions()
options.add_argument('--headless')

#ユーザーエージェントの設定
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
options.add_argument(f'user-agent={user_agent}')
pf_path = r"C:\Users\fu3ka\AppData\Local\Google\Chrome\User Data\Default"
options.add_argument(f'user-data-dir={pf_path}')

driver = webdriver.Chrome(options=options)


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


store_links = []
for i in range(1,3):
    # 1ページ目のURL
    if i==1:
        driver.get("https://r.gnavi.co.jp/area/tokyo/izakaya/rs/")
    else:
    # 2ページ以降のURL
        #次へボタンの画像の親要素を取得
        img_element = driver.find_element(By.CLASS_NAME, "style_nextIcon__M_Me_")
        #親要素のURLを取得
        page_url = img_element.find_element(By.XPATH, "..").get_attribute('href')
        # print(page_url)
        driver.get(page_url)
    
    # それぞれのページの店舗ページURLのリストを取得
    elems = driver.find_elements(By.CLASS_NAME, "style_titleLink__oiHVJ")
    for elem in elems:
        if "PREF" not in elem.get_attribute('href'): #PRを除外
                store_links.append(elem.get_attribute('href'))
    time.sleep(3) #アイドリングタイム
    


#各店舗情報を取得
data=[]
for store_link in store_links[:50]:
    store_res = driver.get(store_link)
    time.sleep(3) #アイドリングタイム

    #店舗の名前取得
    store_name = driver.find_element(By.ID, "info-name").text

    #店舗の電話番号取得
    store_phone = driver.find_element(By.CLASS_NAME, "number").text

    #店舗のメールアドレス取得
    try:
        store_mail_mailto = driver.find_element(By.XPATH, '//a[contains(@href, "mailto:")]').get_attribute("href")
        store_mail = store_mail_mailto.lstrip('mailto:')
    except NoSuchElementException:
        #メールがない場合、空文字を入れる
        store_mail = ""  

    #店舗の住所取得
    region = driver.find_element(By.CLASS_NAME, "region").text
    
    #店舗の建物名取得
    try:
        locality = driver.find_element(By.CLASS_NAME, "locality").text
    except NoSuchElementException:
        #建物名がない場合、空文字を入れる
        locality = ""
    
    #住所を正規表現にする
    prefecture ,city ,street = split_address(region)
    
    final_url = ""
    #URLがない場合は空文字
    try:

        #「お店のホームページ」のURLを取得
        store_url = ""
        elements = driver.find_elements(By.XPATH, "//a[contains(text(), 'お店のホームページ')]")
        if elements:
            store_url = driver.execute_script("return arguments[0].href;", elements[0])
        else:
            #「お店のホームぺージ」がない場合は「オフィシャルページ」のURLを取得
            elements = driver.find_elements(By.XPATH, '//a[contains(@title, "オフィシャルページ")]')
            if elements:
                store_url = driver.execute_script("return arguments[0].href;", elements[0])

        if store_url:
            # JavaScriptで新しいタブを開く
            driver.execute_script(f"window.open('{store_url}', '_blank');")

            # 新しいタブに切り替え
            driver.switch_to.window(driver.window_handles[-1])

            try:
                # 最大20秒待機してURLがリダイレクトするのを確認
                WebDriverWait(driver, 20).until(lambda d: d.current_url != store_url)
                final_url = driver.current_url  # 変化があればリダイレクト先のURLを取得
            except TimeoutException:
                final_url = store_url  # 変化がなければ元のURLをそのまま記録
    except NoSuchElementException:
        final_url = ""
    
    #URLのSSL証明書チェック
    if final_url:
        store_ssl = ssl_check(final_url)
    else:
        store_ssl = ""

    data.append([store_name, store_phone,  store_mail, prefecture, city, street, locality, final_url, store_ssl])


# CSV出力
f = open(r"C:\Users\fu3ka\OneDrive\デスクトップ\Exercise_for_Pool\python\ex1_web-scraping\1-2.csv", mode = 'w', encoding='utf-8-sig', errors='ignore')

writer = csv.writer(f, lineterminator='\n') 
csv_header = ["店舗名","電話番号","メールアドレス","都道府県","市区町村","番地","建物名","URL","SSL"]
writer.writerow(csv_header)
writer.writerows(data)

f.close()





driver.close()