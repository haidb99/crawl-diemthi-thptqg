from Crawl_thanhnien import *
import threading

save_path = 'data'
chrome_path = '../chromedriver_linux64/chromedriver'
so_luong = 500
ma_tinh = '01'


# chrome_options.add_argument("--incognito")
# chrome_options.add_argument("--window-size=1920x1080")
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
Crawler2020('01', chrome_path, save_path)

# t1 = threading.Thread(target = Crawler2020, args=('02', chrome_path, save_path, chrome_options))
# t2 = threading.Thread(target = Crawler2020, args=('04', chrome_path, save_path, chrome_options))
#
#
# t1.start()
# t2.start()
#
# t1.join()
# t2.join()

