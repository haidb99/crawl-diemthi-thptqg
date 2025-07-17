import json

import crawler
from crawler.batch import Batch
import pandas as pd
from utils import cities_code

if __name__ == '__main__':
    crawler = Batch.tuoi_tre(cities_code=cities_code, year=2025, batch_size=5000, crawl_type="sbd")
    crawler.run(is_merge=True)