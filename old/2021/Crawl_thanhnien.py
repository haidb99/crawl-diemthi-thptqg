from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
import re
import time
import os
from bs4 import BeautifulSoup

def Crawler2021(ma_tinh, chrome_path, save_path, so_luong = 9999, start = -1, chrome_options = 0):
    # Neu chua ton tai thi tao thu muc
    try:
        os.mkdir(os.path.join(save_path, ma_tinh))
    except:
        pass

    # set up options
    try:
        thu = chrome_options + 1
        chrome_options = Options()
        # chrome_options.add_argument("--incognito")
        # chrome_options.add_argument("--window-size=1920x1080")

        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    except:
        pass

    driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)

    # url crawl
    print("Watting....")
    url = 'https://thanhnien.vn/giao-duc/tuyen-sinh/2021/tra-cuu-diem-thi-thpt-quoc-gia.html'
    driver.get(url)
    # vi tri bat dau crawl tu
    try:
        list_dir = os.listdir(os.path.join(save_path, ma_tinh))
        try:
            list_dir.remove('.ipynb_checkpoints')
        except ValueError:
            pass


        list_Filename = [int(re.findall('{}(.*)\.csv'.format(ma_tinh), x)[0]) for x in list_dir]
        list_Filename = np.array(list_Filename)
        stt = np.max(list_Filename[list_Filename <= so_luong])
    except:
        stt = -1

    if(start > -1):
        stt = start

    # Khoi tao data
    data = []
    sbd_final = stt
    stt += 1
    time_update = time.time()
    while(1):
        # get sbd
        sbd = ma_tinh + '0' * (4 - len(str(stt))) + str(stt)
        # nhap sbd va an enter
        try:
            description = driver.find_element_by_id('txtkeyword')
            description.clear()
            description.send_keys(sbd, Keys.ENTER)
            time.sleep(0.5)
            html = driver.page_source
            page = BeautifulSoup(html, 'lxml')
        except NoSuchElementException:
            time.sleep(0.1)
            continue

        # get list
        students = []
        list_node = []

        # ----- crawl danh sach --------
        try:
            list_node = page.find('tbody', {'id': 'resultcontainer'}).findAll('tr')
        except:
            pass

        # -----crawl tung hoc sinh ------
        if(len(list_node) > 0):
            for node in list_node:
                monhoc = node.findAll('td')
                std = {}
                if(len(monhoc) == 18):
                    std['SBD'] = monhoc[3].text
                    std['Cum_thi'] = ma_tinh
                    std['Toan'] = monhoc[6].text
                    std['Ngu_van'] = monhoc[7].text
                    std['Ngoai_ngu'] = monhoc[16].text
                    std['Vat_ly'] = monhoc[8].text
                    std['Hoa_hoc'] = monhoc[9].text
                    std['Sinh_hoc'] = monhoc[10].text
                    std['KHTN'] = monhoc[11].text
                    std['Lich_su'] = monhoc[12].text
                    std['Dia_ly'] = monhoc[13].text
                    std['GDCD'] = monhoc[14].text
                    std['KHXH'] = monhoc[15].text
                    students.append(std.copy())

        # them student
        if(len(students) > 0):
            print("{0}..{1}: {2}".format(ma_tinh, stt, len(students)))
            data += students
            sbd_final = stt

        # sau 10' thi lua lai
        if(time.time() - time_update > 600):
            name = ma_tinh + '0' * (4 - len(str(sbd_final))) + str(sbd_final)
            if(len(data) > 0):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            data.clear()
            time_update = time.time()

        # check dieu kien dung
        if(stt > so_luong):
            name = ma_tinh + '0' * (4 - len(str(sbd_final))) + str(sbd_final)
            if(len(data)):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            print('{} Doneeeeeeeeeeeeeeeeee'.format(ma_tinh))
            return

        if(stt - sbd_final > 100):
            name = ma_tinh + '0' * (4 - len(str(sbd_final))) + str(sbd_final)
            if(len(data) > 0):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            print('{} 11111111111111111111111111111111111111111111'.format(ma_tinh))
            return

        # Luot tiep theo
        stt += 1
        # refresh
        if(stt % 50 == 0):
            driver.close()
            driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
            try:
                driver.get(url)
                time.sleep(0.2)
            except WebDriverException:
                print('{} Lagggggggg'.format(ma_tinh))
    driver.close()
