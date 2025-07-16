import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import requests

URLS = [f"https://httpbin.org/delay/1" for _ in range(1000)]  # 100 request delay 1s


# --------------------
# Asyncio + aiohttp
# --------------------
async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def run_asyncio():
    connector = aiohttp.TCPConnector(limit=1000)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, url) for url in URLS]
        for f in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="aiohttp", ascii=" ="):
            await f


# --------------------
# ThreadPool + requests
# --------------------
def fetch_sync(url):
    return requests.get(url).text

def run_threading():
    with ThreadPoolExecutor(max_workers=10000) as executor:
        list(tqdm(executor.map(fetch_sync, URLS), total=len(URLS), desc="threads"))


# --------------------
# Main
# --------------------
if __name__ == "__main__":
    print("===> Bắt đầu benchmark\n")

    t1 = time.time()
    asyncio.run(run_asyncio())
    print(f"\n✅ aiohttp xong trong {time.time() - t1:.2f}s\n")

    t2 = time.time()
    run_threading()
    print(f"\n✅ threading xong trong {time.time() - t2:.2f}s\n")
