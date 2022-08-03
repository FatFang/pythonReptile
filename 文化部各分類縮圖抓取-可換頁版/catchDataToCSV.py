import requests
import time
from concurrent.futures import ThreadPoolExecutor
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

s = Service(r"/Users/gbossfamily/Desktop/爬蟲/chromedriver")
driver = webdriver.Chrome(service=s)


def scrape(urls):
    url = "https://collections.culture.tw/" + urls
    driver.get(url)
    count = driver.find_elements(By.CLASS_NAME, "btn.btn-link.nav-link9.p-0.f-border-b")
    print(len(count))
    final_list = []
    for i in range(len(count)):
        driver.find_element(By.ID, "repEXKIND_btnEXKIND_" + str(i)).click()
        source = driver.page_source
        soup = BeautifulSoup(source, "html.parser")
        name = soup.select('select[id="ddlSYSUNIT"]')
        for n in name:
            nametext = n.select('option[selected="selected"]')
            for nn in nametext:
                if nn.text in final_list:
                    break
                else:
                    final_list.append(nn.text)
        collection = soup.select('div[class="mr-2 rounded mb-1"]')
        for it in collection:
            collect_name = it.select('input')
            collect_quantity = it.select('span')
            for name, quantity in zip(collect_name, collect_quantity):
                # print(name.get('value'), quantity.text)
                final_list.append(name.get('value'))
                final_list.append(quantity.text)
    list_to_csv.append(final_list)
    time.sleep(1)


list_to_csv = []

start = time.time()
main_page_requests = requests.get("https://collections.culture.tw/Unit.aspx")
main_page_result = BeautifulSoup(main_page_requests.text, 'html.parser')

all_organization = main_page_result.select('div[class="UnitBox form-inline"]')  # 各典藏單位名稱
each_organization_href = []  # 各典藏單位網址
for organization in all_organization:
    temps = organization.select('a')
    for temp in temps:
        each_organization_href.append((temp.get('href'))[2:])

for ii in each_organization_href:
    scrape(ii)
'''
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    executor.map(scrape, each_organization_href)
'''
with open("文化部各典藏單位物品分類.csv", 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    for incsv in list_to_csv:
        writer.writerow(incsv)

end = time.time()
print(f"The all time is {end - start}")