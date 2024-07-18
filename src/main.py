import json

import pandas
from crawler.batch import BatchCrawler
import pandas as pd

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    cities_code = ["0{}".format(i) for i in range(10)] + [str(i) for i in range(10, 100)]
    crawler = BatchCrawler(cities_code=cities_code, year=2022)
    crawler.run()
    crawler.concat_files()
    # df = pd.read_csv("data/diemthi_2024.csv", header=0)
    # print(df.count())