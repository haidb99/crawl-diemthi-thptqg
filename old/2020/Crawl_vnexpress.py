from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import numpy as np
import pandas as pd
import re
import time
import os

def Crawler2020(ma_tinh, chrome_path, save_path, so_luong = 999999, start = -1, chrome_options = 0):
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
    url = 'https://diemthi.vnexpress.net/'
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
        stt = 0

    if(start > -1):
        stt = start

    # Khoi tao data
    data = []
    sbd_final = stt
    stt += 1
    time_update = time.time()
    while(1):
        # get sbd
        sbd = ma_tinh + '0' * (6 - len(str(stt))) + str(stt)

        # nhap sbd va an enter
        try:
            description = driver.find_element_by_id('keyword')
            description.clear()
            description.send_keys(sbd, Keys.ENTER)
        except NoSuchElementException:
            time.sleep(0.1)
            continue

        # get list
        student = {}
        t1 = time.time()
        while(1):
            # check dung vong while
            if(time.time() - t1 >= 10):
                break

            list_info = []
            try:
                list_info = driver.find_elements_by_xpath("//td[@class = 'width_sbd']")
            except:
                pass

            # check rong list_info
            if(len(list_info) == 0):
                time.sleep(0.1)
                continue

            # check lay dung SBD
            try:
                student['SBD'] = list_info[0].text
            except:
                student.clear()
                continue

            if(student['SBD'] != sbd):
                time.sleep(0.1)
                continue

            student['Cum_thi'], student['Toan'], student['Ngu_van'], student['Ngoai_ngu'], \
            student['Vat_ly'], student['Hoa_hoc'], student['Sinh_hoc'], student['Diem_KHTN'], \
            student['Lich_su'], student['Dia_ly'], student['GDCD'], student['Diem_KHXH'] = [x.text for x in list_info[1:13]]

            break

        # check student
        if(len(student.keys()) > 1):

            # append student
            print(student)
            data.append((student.copy()))
            sbd_final = stt

        # save
        if(time.time() - time_update > 600):
            name = ma_tinh + '0' * (6 - len(str(sbd_final))) + str(sbd_final)
            if(len(data) > 0):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            data.clear()
            time_update = time.time()

        # hoc sinh tiep theo
        stt += 1

        # refresh
        # if(stt % 50 == 0):
        #     driver.close()
        #     driver = webdriver.Chrome(executable_path=chrome_path, chrome_options=chrome_options)
        #     try:
        #         driver.get(url)
        #         time.sleep(0.2)
        #     except WebDriverException:
        #         print('{} Lagggggggg'.format(ma_tinh))

        # check dieu kien dung
        if(stt > so_luong):
            name = ma_tinh + '0' * (4 - len(str(sbd_final))) + str(sbd_final)
            if(len(data)):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            print('{} Doneeeeeeeeeeeeeeeeee'.format(ma_tinh))
            return

        if(stt - sbd_final > 5):
            name = ma_tinh + '0' * (4 - len(str(sbd_final))) + str(sbd_final)
            if(len(data) > 0):
                pd.DataFrame(data).to_csv(save_path + '/{0}/{1}.csv'.format(ma_tinh, name))
            print('{} 11111111111111111111111111111111111111111111'.format(ma_tinh))
            return
    driver.close()