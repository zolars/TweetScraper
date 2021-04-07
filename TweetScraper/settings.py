# Load configuration from `config.ini`

import configparser

config = configparser.ConfigParser()
config.read("config.ini")

MONGODB_HOST = str(config["MONGODB"]["HOST"])
MONGODB_PORT = int(config["MONGODB"]["PORT"])
MONGODB_DBNAME = "monitor"

GOOGLEMAP_API_KEY = config["API"]["GOOGLEMAP_API_KEY"]

# !!! # Crawl responsibly by identifying yourself (and your website/e-mail) on the user-agent
USER_AGENT = "TweetScraper"

# settings for spiders
BOT_NAME = "TweetScraper"
LOG_LEVEL = "INFO"

SPIDER_MODULES = ["TweetScraper.spiders"]
NEWSPIDER_MODULE = "TweetScraper.spiders"
ITEM_PIPELINES = {
    # "TweetScraper.pipelines.SaveToFilePipeline": 100,
    "TweetScraper.pipelines.SavetoMongoDBPipeline": 100,
}

# settings for where to save data on disk
SAVE_TWEET_PATH = "./output/tweet/"
SAVE_USER_PATH = "./output/user/"

DOWNLOAD_DELAY = 1.0

# settings for selenium
from shutil import which

SELENIUM_DRIVER_NAME = "firefox"
SELENIUM_BROWSER_EXECUTABLE_PATH = which("firefox")
SELENIUM_DRIVER_EXECUTABLE_PATH = which("geckodriver")
SELENIUM_DRIVER_ARGUMENTS = [
    "-headless"
]  # "--headless" if using chrome instead of firefox
DOWNLOADER_MIDDLEWARES = {"scrapy_selenium.SeleniumMiddleware": 800}
