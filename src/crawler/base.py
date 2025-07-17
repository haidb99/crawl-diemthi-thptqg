from abc import ABC, abstractmethod
import asyncio
import json
import os

import aiohttp
import pandas as pd


class BaseCrawler(ABC):
    url_pattern = None
    folder = "data"
    columns_mapping = None

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

    @abstractmethod
    def _get_url_by_sbd(self, sbd: str) -> str:
        pass

    def run(self, is_merge: bool = False):
        asyncio.run(self._run_sync())
        if is_merge:
            self.concat_files()

    @abstractmethod
    async def fetch_data(self, session, url, filename):
        pass

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
