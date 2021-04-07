import json
import logging
import re
from datetime import datetime
from urllib.parse import quote

import requests
from scrapy import http
from scrapy.core.downloader.middleware import DownloaderMiddlewareManager
from scrapy.shell import inspect_response
from scrapy.spiders import CrawlSpider
from scrapy.utils.project import get_project_settings
from scrapy_selenium import SeleniumMiddleware, SeleniumRequest
from TweetScraper.items import Tweet, User
from TweetScraper.utils import language_codes

logger = logging.getLogger(__name__)


class TweetScraper(CrawlSpider):
    name = "TweetScraper"
    allowed_domains = ["twitter.com"]

    def __init__(self, query=''):
        settings = get_project_settings()

        self.url = (f"https://api.twitter.com/2/search/adaptive.json?"
                    f"include_profile_interstitial_type=1"
                    f"&include_blocking=1"
                    f"&include_blocked_by=1"
                    f"&include_followed_by=1"
                    f"&include_want_retweets=1"
                    f"&include_mute_edge=1"
                    f"&include_can_dm=1"
                    f"&include_can_media_tag=1"
                    f"&skip_status=1"
                    f"&cards_platform=Web-12"
                    f"&include_cards=1"
                    f"&include_ext_alt_text=true"
                    f"&include_quote_count=true"
                    f"&include_reply_count=1"
                    f"&tweet_mode=extended"
                    f"&include_entities=true"
                    f"&include_user_entities=true"
                    f"&include_ext_media_color=true"
                    f"&include_ext_media_availability=true"
                    f"&send_error_codes=true"
                    f"&simple_quoted_tweet=true"
                    f"&query_source=typed_query"
                    f"&pc=1"
                    f"&spelling_corrections=1"
                    f"&ext=mediaStats%2ChighlightedLabel"
                    f"&count=20"
                    f"&tweet_search_mode=live")
        self.url = self.url + "&q={query}"
        self.query = query
        self.num_search_issued = 0
        # regex for finding next cursor
        self.cursor_re = re.compile('"(scroll:[^"]*)"')

        self.googleMap_api_key = settings["GOOGLEMAP_API_KEY"]

    def start_requests(self):
        """
        Use the landing page to get cookies first
        """
        yield SeleniumRequest(url="https://twitter.com/explore",
                              callback=self.parse_home_page)

    def parse_home_page(self, response):
        """
        Use the landing page to get cookies first
        """
        # inspect_response(response, self)
        self.update_cookies(response)
        for r in self.start_query_request():
            yield r

    def update_cookies(self, response):
        driver = response.meta["driver"]
        try:
            self.cookies = driver.get_cookies()
            self.x_guest_token = driver.get_cookie("gt")["value"]
            # self.x_csrf_token = driver.get_cookie("ct0")["value"]
        except:
            logger.info("cookies are not updated!")

        self.headers = {
            "authorization":
            "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-guest-token": self.x_guest_token,
            # "x-csrf-token": self.x_csrf_token,
        }
        print("headers:\n--------------------------\n")
        print(self.headers)
        print("\n--------------------------\n")

    def start_query_request(self, cursor=None):
        """
        Generate the search request
        """
        if cursor:
            url = self.url + "&cursor={cursor}"
            url = url.format(query=quote(self.query), cursor=quote(cursor))
        else:
            url = self.url.format(query=quote(self.query))
        request = http.Request(url,
                               callback=self.parse_result_page,
                               cookies=self.cookies,
                               headers=self.headers)
        yield request

        self.num_search_issued += 1
        if self.num_search_issued % 100 == 0:
            # get new SeleniumMiddleware
            for m in self.crawler.engine.downloader.middleware.middlewares:
                if isinstance(m, SeleniumMiddleware):
                    m.spider_closed()
            self.crawler.engine.downloader.middleware = DownloaderMiddlewareManager.from_crawler(
                self.crawler)
            # update cookies
            yield SeleniumRequest(url="https://twitter.com/explore",
                                  callback=self.update_cookies,
                                  dont_filter=True)

    def parse_result_page(self, response):
        """
        Get the tweets & users & next request
        """
        # inspect_response(response, self)

        # handle current page

        data = json.loads(response.text)

        users = {}
        for user in self.parse_user_item(data["globalObjects"]["users"]):
            users[user["user_id"]] = user
            yield user

        for tweet in self.parse_tweet_item(
                data["globalObjects"]["tweets"],
                users,
        ):
            yield tweet

        # get next page
        cursor = self.cursor_re.search(response.text).group(1)
        for r in self.start_query_request(cursor=cursor):
            yield r

    def parse_user_item(self, user_items):
        for _, user_item in user_items.items():
            user = User()
            user["created_at"] = datetime.strptime(
                user_item["created_at"],
                "%a %b %d %H:%M:%S %z %Y",
            )

            user["user_id"] = user_item["id"]
            user[
                "user_profile_url"] = f'https://twitter.com/{user_item["screen_name"]}'
            user["user_name"] = user_item["screen_name"]
            user["user_screen_name"] = user_item["name"]
            user["user_bio"] = user_item["description"]
            user["user_followers"] = user_item["followers_count"]
            user["user_following"] = user_item["friends_count"]
            user["user_listed"] = user_item["listed_count"]

            try:
                location_str = user_item["location"]

                response = requests.get(
                    f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?key={self.googleMap_api_key}&input={location_str}&inputtype=textquery&language=en&fields=place_id"
                )
                place_id = response.json()["candidates"][0]["place_id"]
                response = requests.get(
                    f"https://maps.googleapis.com/maps/api/place/details/json?key={self.googleMap_api_key}&place_id={place_id}&language=en"
                )
                place_details = response.json()["result"]["address_components"]

                for item in place_details:
                    long_name = item["long_name"]
                    if item["types"][0] == "country":
                        user["country"] = long_name
                    elif item["types"][0] == "administrative_area_level_1":
                        user["state"] = long_name
                    elif item["types"][0] == "administrative_area_level_2":
                        user["city"] = long_name
            except IndexError:
                pass

            yield user

    def parse_tweet_item(
        self,
        tweet_items,
        users,
    ):
        for _, tweet_item in tweet_items.items():

            tweet = Tweet()
            user = users[tweet_item["user_id"]]

            tweet["created_at"] = datetime.strptime(
                tweet_item["created_at"],
                "%a %b %d %H:%M:%S %z %Y",
            )

            tweet[
                "url"] = f"https://twitter.com/{user['user_name']}/status/{tweet_item['id']}"
            tweet["tweet_id"] = tweet_item["id"]
            tweet["content"] = tweet_item["full_text"]
            tweet["language"] = language_codes[tweet_item["lang"]]
            try:
                tweet["tweet_client"] = re.search(
                    ">(.*?)<",
                    tweet_item["source"],
                ).group(1)
            except AttributeError:
                tweet["tweet_client"] = None

            tweet["retweet_count"] = tweet_item["retweet_count"]
            tweet["favorite_count"] = tweet_item["favorite_count"]
            tweet["reply_count"] = tweet_item["reply_count"]
            tweet["quote_count"] = tweet_item["quote_count"]

            tweet["in_reply_to_status_id"] = tweet_item[
                "in_reply_to_status_id"]
            tweet["in_reply_to_user_id"] = tweet_item["in_reply_to_user_id"]

            tweet["user"] = user

            with open(f"output/{tweet['tweet_id']}.json", "w+") as fp:
                json.dump(tweet_item, fp)

            yield tweet
