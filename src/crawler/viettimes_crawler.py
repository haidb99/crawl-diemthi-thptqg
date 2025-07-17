import asyncio
import json
import os

import aiohttp
import pandas as pd


class ViettimeCrawler:
    url_pattern = "https://api.viettimes.vn/api/diem-thi?type=0&keyword={keyword}&kythi=THPT&nam={year}&cumthi=0"
    folder = "data"
    columns_mapping = {
        "sbd": "so_bao_danh",
        "ngaySinh": "ngay_sinh",
        "hoTen": "ho_ten",
        "dm01": "toan",
        "dm02": "ngu_van",
        "dm03": "vat_ly",
        "dm04": "hoa_hoc",
        "dm05": "sinh_hoc",
        "dm06": "dm06",
        "dm07": "ngoai_ngu",
        "dm08": "lich_su",
        "dm09": "dia_ly",
        "dm10": "gdcd",
        "dmText": "ma_ngoai_ngu"
    }

    def __init__(self, cities_code: list, year: int = 2024, batch_size=5000):
        """
        Initialize an instance of the class.

        Parameters:
        city_code (str): city codes.
        year (int): The year to be used, default is 2024.
        """
        self.year = year
        self.cities_code = cities_code
        self.batch_size = batch_size
        try:
            os.makedirs(f"data/{self.year}/")
        except FileExistsError:
            pass
        self.filename_pattern = f"data/{self.year}/" + "{city_code}.json"
        self.semaphore = asyncio.Semaphore(self.batch_size)
        self.lock = asyncio.Lock()

    def run(self, is_merge: bool = False):
        asyncio.run(self._run_sync())
        if is_merge:
            self.concat_files()

    async def _run_sync(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for city_code in self.cities_code:
                last_group = await self._get_last_group(session, city_code)
                tasks.extend([self._get_data_by_group(session, city_code, group) for group in range(last_group + 1)])
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _get_data_by_group(self, session, city_code, group):
        keyword = self._get_group(city_code, group)
        url = self.url_pattern.format(keyword=keyword, year=self.year)
        filename = self.filename_pattern.format(city_code=city_code)
        print(filename)
        await self.fetch_data(session, url, filename)

    def _get_group(self, city_code: str, number: int):
        return f"{city_code}{'{:04}'.format(number)}"

    async def _get_last_group(self, session, city_code):
        _min = 0
        _max = 9999
        if not await self._is_valid_group(session, self._get_group(city_code, _min)):
            return 0
        if await self._is_valid_group(session, self._get_group(city_code, _max)):
            return _max

        while True:
            _mid = (_min + _max) // 2
            if await self._is_valid_group(session, self._get_group(city_code, _mid)):
                _min = _mid
            else:
                _max = _mid
            if _max - _min == 1:
                break

        return _min

    async def _is_valid_group(self, session, keyword):
        async with self.semaphore:
            async with session.get(self.url_pattern.format(keyword=keyword, year=self.year)) as response:
                if len(json.loads(await response.text()).get("data", {}).get("results")) > 0:
                    return True
        return False

    async def fetch_data(self, session, url, filename):
        async with self.semaphore:
            async with session.get(url) as response:
                print(response.url)
                raw = await response.text()
                data = json.loads(raw).get("data", {}).get("results", [])
                if len(data) > 0:
                    output = "\n".join(json.dumps(node, ensure_ascii=False) for node in data)
                    async with self.lock:
                        with open(filename, 'a') as f:
                            f.write(output + '\n')

    def concat_files(self):
        dfs = []
        for city_code in self.cities_code:
            path_temp = self.filename_pattern.format(city_code=city_code)
            try:
                df_temp = pd.read_json(path_temp, lines=True)
                dfs.append(df_temp)
            except FileNotFoundError:
                print("File {} not found".format(path_temp))
        df_result = pd.concat(dfs)
        df_result = df_result.rename(columns=self.columns_mapping)
        df_result.to_csv("data/diemthi_{}.csv".format(self.year), index=False, header=True)
