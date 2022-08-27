import requests
import time
import os
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


# 功能：下載圖片
# argument: url_image(縮圖網址) organ(該藏品收藏之館名) name(該藏品之名稱) save_path(該藏品之儲存路徑)
def getimage(url_image, organ, name, save_path):
    img_ = requests.get("https://collections.culture.tw/" + url_image)  # 網頁requests並回傳圖片
    img_name = save_path + organ + '-' + name  # 檔案名稱(路徑/機構-名稱[順序].jpg)
    # print(save_path)
    # print(img_name)  # check filename
    with open(img_name + '.jpg', "wb") as file:  # 創建檔案
        file.write(img_.content)  # 寫入檔案


# 造訪各類別網頁
# argument: urlss(該分類藏品總合集的網址) path(縮圖儲存之資料夾路徑) organize_class_name(該分類之名稱)
def each(urlss, path, organize_class_name):
    print(path)
    path_tmp = []  # 給多執行緒的路徑list
    driver.get(urlss)  # 程式自動開啟Google Chrome前往urlss其網址

    driver.find_element(By.XPATH,"//*[@id='GridView1']/tbody/tr/td/table/tbody/tr/td[7]/input").click()  # 點擊頁數快捷鍵投鍵，前往最後一頁
    count = int(driver.find_element(By.XPATH, '//*[@id="GridView1"]/tbody/tr/td/table/tbody/tr/td[7]/span').text)  # 取得此類別共有多少頁
    print(f'This class has {count} pages')
    driver.find_element(By.XPATH, '//*[@id="GridView1"]/tbody/tr/td/table/tbody/tr/td[1]/input').click()  # 返回第一頁

    button_pos = 1  # 控制按鈕<td>之位置
    page_control = True  # 第一頁與其他頁不同 設此布林值去控制
    broken_page = False  # 是否有破圖網頁(經證實在建築圖此分類下第1246頁是有問題的 -> 網頁程式碼問題)
    page_big_six = True  # 若總頁數小於五頁 -> 不需要去搜尋'...'按鍵
    if organize_class_name == '建築圖':
        broken_page = True
    if count < 6:
        page_big_six = False 

    while True:  # 下載圖片之迴圈
        # page(1)
        # td位置     1 2 3 4 5  6  7
        # 按鈕 ->    1 2 3 4 5 ... >>
        # other page
        # td位置      1  2  3 4 5 6  7   8   9
        # 按鈕 ->    << ... 6 7 8 9 10  ... >>
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

        source = driver.page_source  # 取得網頁原始碼
        soup = BeautifulSoup(source, "html.parser")  # 取得網頁原始碼
        a_elem = soup.select('a[class="d-block"]')  # 選擇縮圖之元素
        image = []  # 圖片網址
        organ = []  # 機構
        name = []  # 名稱

        for num in range(len(a_elem)):  # 依照一頁有幾張圖去跑loop
            image.append(((a_elem[num].select('img'))[0].get('src'))[2:])  # 將圖片網址加入list
            organ_tmp = a_elem[num].select(
                'div[class="departments"]')  # 先搜尋最基本的class = departments 若有兩間以上則叫departments2...
            class_num_organ = 2
            while not len(organ_tmp):  # len of list = 0 -> 沒搜尋到
                organ_tmp = (a_elem[num].select('div[class="departments' + str(class_num_organ) + '"]'))  # 由2開始找
                class_num_organ += 1  # 增加位數 以防再搜尋不到
                # print("organ while")
            organ.append(organ_tmp[0].text)  # 將物品之機構名稱加入list

            name_a_tmp = a_elem[num].select('div[class="works"]')  # 同departments作法
            class_num_name = 2
            while not len(name_a_tmp):
                name_a_tmp = a_elem[num].select('div[class="works' + str(class_num_name) + '"]')
                class_num_name += 1
                # print("name while")
            name_a = name_a_tmp[0].text  # name_a 儲存物品名稱
            name_a_temp = name_a  # temp 儲存name_a的原始名稱
            name_a_count = 2  # 重複順序由2開始
            while name_a in all_name:  # 如果該物品名稱+順序已經出現在list裡則增加順序並檢查以免名稱重複導致檔案被覆寫
                # print("Enter while loop success")
                name_a = name_a_temp  # 重置name_a名稱
                name_a = name_a + str(name_a_count)  # 名稱+順序
                name_a_count += 1  # 順序加一
            all_name.append(name_a)  # 將物品之名稱加入list
            name.append(name_a)  # 將物品之名稱加入list
            path_tmp.append(path)

        with ThreadPoolExecutor() as executor:  # 多執行緒以減少下載圖片時間
            executor.map(getimage, image, organ, name, path_tmp)  # 同時下載圖片
        if int(button_num.text) == count and not page_big_six:
            break
        if int(button_num.text) == count:  # 若頁面全部跑完則跳出迴圈
            break
        time.sleep(2.5)
    all_name.clear()  # 清空list
    time.sleep(3)


# Chrome driver 前置作業
s = Service(r"/Users/gbossfamily/Desktop/爬蟲/chromedriver")  # 若不同裝置則path不一樣
driver = webdriver.Chrome(service=s)

path_now = os.getcwd()  # 取得當前路徑
mkdir(path_now + "/image")  # 在目前程式資料夾底下建立目錄名為image的資料夾

main_page_requests = requests.get("https://collections.culture.tw/Class.aspx")  # 進入主網頁
main_page_result = BeautifulSoup(main_page_requests.text, 'html.parser')  # 回傳網頁原始碼 -> 收集資料

# start search
all_main_class = main_page_result.select('div[class="col-12 mb-4"]')  # 取得大分類之名稱
all_main_class.pop(0)  # 刪除收集資料發現的空內容
for i in all_main_class:  # 依序拜訪大分類
    title_elem = i.select('h2[class="ClassTypeTitle d-block mb-1"]')   # 取得大分類所有之名稱
    if not len(title_elem):
        # print("test")
        title_elem = i.select('h2[class="ClassTypeTitle d-block"]')
    # print(title_elem[0].text)
    mkdir(path_now + "/image/" + title_elem[0].text)
    urls = i.select('a[class="ClassBoxItem d-flex align-items-center justify-content-center"]')
    for j in urls:
        # print(j.get('href'))
        # print(j.text.strip())
        mkdir(path_now + "/image/" + title_elem[0].text + "/" + j.text.strip())
        # print(str(j.get('href')), path_now + "/image/" + title_elem[0].text + "/" + j.text.strip() + "/")
        path_complete = path_now + "/image/" + title_elem[0].text + "/" + j.text.strip() + "/"
        each("https://collections.culture.tw/" + str(j.get('href')), path_complete, j.text.strip())
        time.sleep(5)

time.sleep(5)
driver.quit()  # 退出