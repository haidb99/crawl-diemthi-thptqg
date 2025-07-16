import asyncio
import json
import os
import aiohttp
import pandas as pd

from crawler.base import BaseCrawler
from utils import setup_logger
from typing import Literal
from tqdm.asyncio import tqdm_asyncio

logger = setup_logger(__name__)

class TuoiTreCrawler(BaseCrawler):
    url_base = "https://s6.tuoitre.vn/api/diem-thi-thpt.htm"
    url_pattern = "https://s6.tuoitre.vn/api/diem-thi-thpt.htm?sbd={sbd}&year={year}"
    folder = "data"
    columns_mapping = {
        "SBD": "so_bao_danh",
        "TinhId": "city_code",
        "NGAY_SINH": "ngay_sinh",
        "file_name": "ho_ten",
        "TOAN": "toan",
        "VAN": "ngu_van",
        "LI": "vat_ly",
        "HOA": "hoa_hoc",
        "SINH": "sinh_hoc",
        "NGOAI_NGU": "ngoai_ngu",
        "MA_MON_NGOAI_NGU": "ma_ngoai_ngu",
        "SU": "lich_su",
        "DIA": "dia_ly",
        "GIAO_DUC_CONG_DAN": "gdcd",
        "GDKT_PL": "gdkt_pl",
        "TIN_HOC": "tin_hoc",
        "CN_CONG_NGHIEP": "cn_cong_nghiep",
        "CN_NONG_NGHIEP": "cn_nong_nghiep",
        "TONGDIEM": "tong_diem",
    }

    def __init__(self, cities_code: list, year: int = 2025, batch_size=5000, crawl_type: Literal["page", "sbd"] = "page"):
        super().__init__(cities_code, year, batch_size)
        self.semaphore = asyncio.Semaphore(self.batch_size)
        self.crawl_type = crawl_type
        self.page_size = 100

    def run(self, is_merge: bool = False):
        logger.info(f"start crawler")
        asyncio.run(self._run_sync())
        if is_merge:
            self.concat_files()
        logger.info(f"end crawler")

    async def _run_sync(self):
        async with aiohttp.ClientSession() as session:
            tasks = [self._get_data_by_city_code(session, city_code) for city_code in self.cities_code]
            rs = await asyncio.gather(*tasks, return_exceptions=True)
            for r in rs:
                if isinstance(r, Exception):
                    logger.error(f"Error occurred: {r}")
                else:
                    pass
                    # logger.info(f"Data fetched successfully for city code: {r}")

    def _is_exist_file(self, city_code: str):
        import os
        filename = self._get_filename_by_city_code(city_code)
        return os.path.exists(filename)
    
    def _get_url_by_sbd(self, sbd):
        return self.url_pattern.format(sbd=sbd, year=self.year)

    def _get_param_by_page(self, city_code, page=1) -> dict:
        params = {
            "year": self.year,
            "size": self.page_size,
            "district": city_code,
            "pageindex": page,
        }
        return params

    def _get_filename_by_city_code(self, city_code):
        return self.filename_pattern.format(city_code=city_code)

    def _get_sbd_by_city_code(self, city_code: str, stt: int):
        if len(city_code) == 1:
            _city_code = f"0{city_code}"
        elif len(city_code) == 2:
            _city_code = city_code
        else:
            raise ValueError(f"Invalid city code: {city_code}")
        sbd = f"{stt:06d}"
        return f"{_city_code}{sbd}"

    async def _get_data_by_city_code(self, session, city_code):
        if self._is_exist_file(city_code):
            logger.info(f"File for city code {city_code} already exists, skipping...")
            return city_code
        if self.crawl_type == "page":
            last_page = await self._get_last_page(session, city_code)

            tasks = [self._get_data_by_page(session, city_code, page) for page in range(0, last_page + 1)]
            results = await tqdm_asyncio.gather(*tasks, desc=f"{city_code} - pages", ascii=" =")
            self.save_data(results, city_code)
            return city_code
        elif self.crawl_type == "sbd":
            last_stt = await self._get_last_stt(session, city_code)
            if last_stt < 1:
                return city_code
            tasks = [self._get_data_by_sbd(session, city_code, stt) for stt in range(0, last_stt + 1)]
            results = await tqdm_asyncio.gather(*tasks, desc=f"{city_code} - SBD", ascii=" =")
            self.save_data(results, city_code)
            return city_code

    async def _get_data_by_page(self, session, city_code: str, page: int):
        params = self._get_param_by_page(city_code, page)
        url = self.url_base
        raw = await self.fetch_data(session, url, params)
        if not raw:
            logger.error(f"Failed to fetch data for city code {city_code} on page {page}")
            return []
        return raw.get("data", [])

    async def _get_data_by_sbd(self, session, city_code: str, stt: int):
        sbd = self._get_sbd_by_city_code(city_code, stt)
        url = self._get_url_by_sbd(sbd)
        raw = await self.fetch_data(session, url)
        if not raw:
            logger.error(f"Failed to fetch data for city code {city_code} on page {stt}")
            return []
        return raw.get("data", [])

    def save_data(self, data: list[dict], city_code: str):
        if len(data) == 0:
            return
        if len(data) == 1 and data[0] == {}:
            return
    
        with open(self.filename_pattern.format(city_code=city_code), "w") as f:
            for result in data:
                if isinstance(result, dict):
                    json.dump(result, f, ensure_ascii=False)
                    f.write("\n")
                if isinstance(result, list):
                    if len(result) == 0:
                        continue
                    for item in result:
                        json.dump(item, f, ensure_ascii=False)
                        f.write("\n")

    async def _get_last_stt(self, session, city_code):
        async def _is_valid_sbd(session, city_code, sbd):
            sbd = self._get_sbd_by_city_code(city_code, sbd)
            url = self._get_url_by_sbd(sbd)
            raw = await self.fetch_data(session, url)
            return raw.get("data", []) != []

        _min = 1
        _max = 999999
        if not await _is_valid_sbd(session, city_code, _min):
            return 0
        if await _is_valid_sbd(session, city_code, _max):
            return _max

        while True:
            _mid = (_min + _max) // 2
            if await _is_valid_sbd(session, city_code, _mid):
                _min = _mid
            else:
                _max = _mid
            if _max - _min == 1:
                break

        # logger.info(f"Last STT for city code {city_code} is {_min}")
        return _min
    

    
    async def _get_last_page(self, session, city_code):
        params = self._get_param_by_page(city_code)
        url = self.url_base
        raw = await self.fetch_data(session, url, params)
        total = raw.get("total", 0)
        return total // self.page_size + 1

    async def fetch_data(self, session, url, params=None):
        
        async with self.semaphore:
            async def _fetch(session, url, params=None):
                async with session.get(url, params=params) as response:
                    # logger.info(f"Fetching data from {response.url}")
                    if response.status == 429 or response.status == 502:
                        await asyncio.sleep(0.5)
                        return await _fetch(session, url, params)
                    elif response.status != 200:
                        logger.error(f"Failed to fetch data from {url}, status code: {response.status}")
                        return {}
                    return json.loads(await response.text())
            return await _fetch(session, url, params)

    def concat_files(self):
        dfs = []
        for file in os.listdir(f"{self.folder}/{self.year}"):
            if not file.endswith(".json"):
                continue

            path_temp = os.path.join(f"{self.folder}/{self.year}", file)
            try:
                df_temp = pd.read_json(path_temp, lines=True)
                dfs.append(df_temp)
            except ValueError as e:
                logger.error(f"Error reading {path_temp}: {e}")

        df_result = pd.concat(dfs)
        df_result = df_result.rename(columns=self.columns_mapping)[self.columns_mapping.values()]
        df_result.to_csv("data/diemthi_{}.csv".format(self.year), index=False, header=True)
