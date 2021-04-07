import os
import sys

from scrapy.cmdline import execute

dirpath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(dirpath)

execute([
    'scrapy',
    'crawl',
    'TweetScraper',
    '-a',
    "query=\"Do it for our country's pride .....do it for our brave INDIAN ARMY\"",
])
