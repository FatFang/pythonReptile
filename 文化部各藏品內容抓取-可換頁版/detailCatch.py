import requests
import time
import os
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from concurrent.futures import ThreadPoolExecutor

all_name = []  # 全域list 儲存同機構所有典藏物品名稱，以方便檢查是否名稱重複

def mkdir(path):
    # 判斷目錄是否存在 存在：True 不存在：False
    folder = os.path.exists(path)
    if not folder:
        # 如果不存在，則建立新目錄
        os.makedirs(path)
        print(f'{path} create successful')
    else:
        # 如果目錄已存在，則不建立，提示目錄已存在
        print(f'{path} is exist')
#class="col-12 col-xl-6 col-lg-6 mb-2 p-2 p-xl-5 p-lg-5 p-md-5 bg-white h-100"


def Getimage(url_image, name, organ, save_path):
    img_ = requests.get(url_image)  # 網頁requests並回傳圖片
    img_name = save_path + organ + '-' + name  # 檔案名稱(路徑/機構-名稱[順序].jpg)
    # print(save_path)
    # print(img_name)  # check filename
    with open(img_name + '.jpg', "wb") as file:  # 創建檔案
        file.write(img_.content)  # 寫入檔案


def Detail(collect_url, collect_name, collect_organ, save_path):
    # print(collect_url)
    detail_main_page = requests.get(collect_url)    
    detail_main_page_result = BeautifulSoup(detail_main_page.text, 'html.parser')
    a = detail_main_page_result.select('div[class="col-12 col-xl-6 col-lg-6 mb-2 p-0 pl-xl-5 pl-lg-5 pr-xl-5 pr-lg-5"]')
    b = a[0].select('div[class="form-row"]')
    c = b[0].select('div[class="col-12"]')
    d = c[0].select('ul[id="TreeView1"]')

    a2 = detail_main_page_result.select('div[class="col-12 col-xl-6 col-lg-6 mb-2 p-2 p-xl-5 p-lg-5 p-md-5 bg-white h-100"]')
    b2 = a2[0].select('img[class="img-fluid"]')
    image_src = str(b2[0].get('src'))
    print(image_src)
    # check_ul_or_div = True
    if len(d) == 0:
        collect_data_list = []
        collect_data_dict = {}
        div_elem = c[0].select('div[class="mt-1"]')
        for i in div_elem:
            collect_data_list.append(i.text)
        # print(collect_data)
        for i in range(len(collect_data_list)):
            collect_data_dict[i] = collect_data_list[i]
        with open(save_path + collect_organ + '-' + collect_name + '.json', 'w', encoding="utf-8") as fp:
            json.dump(collect_data_dict, fp, indent=4, ensure_ascii=False)
    else:
        collect_data = {}
        li_elem = d[0].select('li')
        for i in li_elem:
            li_li_elem = i.select('li[class="downitem"]')
            for j in li_li_elem:
                span_elem = j.select('span')
                font_elem = j.select('font')
                space_char = "\u3000"
                font_text = font_elem[0].text
                if space_char in font_elem[0].text:
                    font_text = font_text.replace(space_char, '')
                collect_data[span_elem[0].text] = font_text
    # print(collect_data)
        with open(save_path + collect_organ + '-' + collect_name + '.json', 'w', encoding="utf-8") as fp:
            json.dump(collect_data, fp, indent=4, ensure_ascii=False)
    Getimage(image_src ,collect_name, collect_organ, save_path)



def catchDetail(url, save_mkdir, class_name):
    driver.get(url)

    driver.find_element(By.XPATH,"//*[@id='GridView1']/tbody/tr/td/table/tbody/tr/td[7]/input").click()  # 點擊頁數快捷鍵投鍵，前往最後一頁
    count = int(driver.find_element(By.XPATH, '//*[@id="GridView1"]/tbody/tr/td/table/tbody/tr/td[7]/span').text)  # 取得此類別共有多少頁
    print(f'This class has {count} pages')
    driver.find_element(By.XPATH, '//*[@id="GridView1"]/tbody/tr/td/table/tbody/tr/td[1]/input').click()  # 返回第一頁

    button_pos = 1  # 控制按鈕<td>之位置
    page_control = True  # 第一頁與其他頁不同 設此布林值去控制
    broken_page = False  # 是否有破圖網頁(經證實在建築圖此分類下第1246頁是有問題的 -> 網頁程式碼問題)
    page_big_six = True  # 若總頁數小於五頁 -> 不需要去搜尋'...'按鍵
    if class_name == '建築圖':
        broken_page = True
    if count < 6:
        page_big_six = False 

    while True:
        if button_pos > 6 and page_control:  # 若第一頁的(...)按鈕被按後進入第二頁
            button_pos = 3  # 按鈕開始位置由td[3]開始
            page_control = False  # 將不再執行第一頁之程序
        if button_pos > 8 and not page_control:  # 第二開始至最後一頁的程序
            button_pos = 3  # 按鈕開始位置由td[3]開始

        driver.find_element(By.XPATH, "//*[@id='GridView1']/tbody/tr/td/table/tbody/tr/td[" + str(button_pos) + "]").click()  # 尋找下一頁按鈕並點擊

        if button_pos == 8 and not page_control or button_pos == 6 and page_control:  # 若是點擊(...)鍵則不讀取照片
            button_pos += 1
            continue

        button_num = driver.find_element(By.XPATH, "//*[@id='GridView1']/tbody/tr/td/table/tbody/tr/td[" + str(button_pos) + "]/span")  # 取得頁面之頁數
        button_pos += 1
        print("%d" % int(button_num.text), end='\r')  # 萬一因時間過長而被ban或突發原因可知當時跑到哪裡

        if int(button_num.text) == 1246 and broken_page:
            continue
        
        this_page_collect_urls = []
        this_page_names = []
        this_page_organs = []
        this_page_save_paths = []
        source = driver.page_source  # 取得網頁原始碼
        soup = BeautifulSoup(source, "html.parser")  # 取得網頁原始碼
        collection_elem = soup.select('a[class="d-block"]')  # 選擇縮圖之元素
        for j in collection_elem:
            this_page_collect_urls.append("https://collections.culture.tw/" + str((j.get('href'))[2:]))

            name_a = str(j.get("title"))  # name_a 儲存物品名稱
            name_a_temp = name_a  # temp 儲存name_a的原始名稱
            name_a_count = 2  # 重複順序由2開始
            while name_a in all_name:  # 如果該物品名稱+順序已經出現在list裡則增加順序並檢查以免名稱重複導致檔案被覆寫
                # print("Enter while loop success")
                name_a = name_a_temp  # 重置name_a名稱
                name_a = name_a + str(name_a_count)  # 名稱+順序
                name_a_count += 1  # 順序加一
            all_name.append(name_a)  # 將物品之名稱加入list
            this_page_names.append(name_a)

            organ_tmp = j.select('div[class="departments"]')  # 先搜尋最基本的class = departments 若有兩間以上則叫departments2...
            class_num_organ = 2
            while not len(organ_tmp):  # len of list = 0 -> 沒搜尋到
                organ_tmp = (j.select('div[class="departments' + str(class_num_organ) + '"]'))  # 由2開始找
                class_num_organ += 1  # 增加位數 以防再搜尋不到
                # print("organ while")
            this_page_organs.append(organ_tmp[0].text)  # 將物品之機構名稱加入list
            this_page_save_paths.append(save_mkdir)
        start = time.time()
        with ThreadPoolExecutor() as executor:  # 多執行緒以減少下載圖片時間
            executor.map(Detail, this_page_collect_urls, this_page_names, this_page_organs, this_page_save_paths)  # 同時下載圖片
        end = time.time()
        print(end - start)
        if int(button_num.text) == count and not page_big_six:
            break
        if int(button_num.text) == count:  # 若頁面全部跑完則跳出迴圈
            break
        time.sleep(2.5)
        # for j in range(len(this_page_names)):
            # print(this_page_collect_urls[j], this_page_names[j], this_page_organs[j])
        # break
    all_name.clear()  # 清空list
    time.sleep(3)



s = Service(r"/Users/gbossfamily/Documents/git/pythonReptile/文化部各藏品內容抓取-可換頁版/chromedriver")  # 若不同裝置則path不一樣
driver = webdriver.Chrome(service=s)

path_now = os.getcwd()  # 取得當前路徑
mkdir(path_now + "/detail")

all_urls = []
all_save_paths = []
all_class_name = []

main_page_requests = requests.get("https://collections.culture.tw/Class.aspx")  # 進入主網頁
main_page_result = BeautifulSoup(main_page_requests.text, 'html.parser')  # 回傳網頁原始碼 -> 收集資料

all_main_class = main_page_result.select('div[class="col-12 mb-4"]')  # 取得大分類之名稱
all_main_class.pop(0)  # 刪除收集資料發現的空內容
for i in all_main_class:  # 依序拜訪大分類
    title_elem = i.select('h2[class="ClassTypeTitle d-block mb-1"]')   # 取得大分類所有之名稱
    if not len(title_elem):
        title_elem = i.select('h2[class="ClassTypeTitle d-block"]')
    # print(title_elem[0].text)
    mkdir(path_now + "/detail/" + title_elem[0].text)
    urls = i.select('a[class="ClassBoxItem d-flex align-items-center justify-content-center"]')
    for j in urls:
        path_complete = path_now + "/detail/" + title_elem[0].text + "/" + j.text.strip()
        mkdir(path_complete)
        url_complete = "https://collections.culture.tw/" + str((j.get('href'))[2:])
        all_urls.append(url_complete)
        all_save_paths.append(path_complete + "/")
        all_class_name.append(j.text.strip())
# print(len(all_urls))
# print(len(all_save_paths))
# print(len(all_class_name))

# 控制尋找類別的迴圈
for i in range(71):
    print(1)
    # print(all_urls[i], all_save_paths[i], all_class_name[i])
    catchDetail(all_urls[i], all_save_paths[i], all_class_name[i])
    # break

driver.quit()  # 退出
