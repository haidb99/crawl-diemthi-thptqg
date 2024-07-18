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

def Crawl_thanhnien_bosung(list_miss, chrome_path, save_path, chrome_options = 0):
    # Neu chua ton tai thi tao thu muc
    try:
        os.mkdir(os.path.join(save_path, 'Miss'))
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

    data = []
    list_none = []
    for sbd in list_miss:
        # ----sbd : string ----
        sbd = str(sbd)
        if(len(sbd) == 5):
            sbd = '0' + sbd

        # get list
        students = []
        list_node = []
        # -------crawl -------
        description = driver.find_element_by_id('txtkeyword')
        description.clear()
        description.send_keys(sbd, Keys.ENTER)
        time.sleep(1)
        html = driver.page_source
        page = BeautifulSoup(html, 'lxml')

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
                    std['Cum_thi'] = sbd[:2]
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
            print("{0}: {1}".format(sbd, len(students)))
            data += students
        else:
            list_none.append(sbd)

    # crawl xong----------------------luu lai ket qua----------------
    if(len(data) > 0):
        pd.DataFrame(data).to_csv(save_path + '/{0}'.format("missing.csv"))
        print('--------Doneeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee!----------')
        print(list_none)
