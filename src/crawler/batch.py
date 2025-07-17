

from crawler.tuoi_tre_crawler import TuoiTreCrawler
from crawler.viettimes_crawler import ViettimeCrawler


class Batch:
    viettimes: ViettimeCrawler = ViettimeCrawler
    tuoi_tre: TuoiTreCrawler = TuoiTreCrawler
