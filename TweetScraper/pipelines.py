import json
import logging
import os

import pymongo
from scrapy.utils.project import get_project_settings

from TweetScraper.items import Tweet, User
from TweetScraper.utils import mkdirs

logger = logging.getLogger(__name__)


class SavetoMongoDBPipeline(object):
    """ pipeline that save data to MongoDB """
    def __init__(self):
        settings = get_project_settings()

        # connect to MongoDB server
        host = settings["MONGODB_HOST"]
        port = settings["MONGODB_PORT"]
        db = settings["MONGODB_DBNAME"]
        self._client = pymongo.MongoClient(f"mongodb://{host}:{port}/")
        self._db = self._client[db]

    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            try:
                col = self._db["base"]
                # col.insert_one({
                #     "Collected Date":
                #     item["collected_at"],
                #     "Date":
                #     item["created_at"],
                #     "URL":
                #     item["url"],
                #     "Hit Sentence":
                #     item["content"],
                #     "Source":
                #     "Twitter",
                #     "Influencer":
                #     "@" + item["user"]["user_name"],
                #     "Country":
                #     item["user"]["country"],
                #     "Language":
                #     item["language"],
                #     "Reach":
                #     item["retweet_count"] + item["favorite_count"] +
                #     item["reply_count"] + item["quote_count"],
                #     "Tweet Id":
                #     item["tweet_id"],
                #     "Twitter Id":
                #     item["user"]["user_id"],
                #     "Twitter Client":
                #     item["tweet_client"],
                #     "Twitter Screen Name":
                #     item["user"]["user_screen_name"],
                #     "User Profile Url":
                #     item["user"]["user_profile_url"],
                #     "Twitter Bio":
                #     item["user"]["user_bio"],
                #     "Twitter Followers":
                #     item["user"]["user_followers"],
                #     "Twitter Following":
                #     item["user"]["user_following"],
                #     "State":
                #     item["user"]["state"],
                #     "City":
                #     item["user"]["city"],
                # })
            except Exception as err:
                logger.debug(err)
            logger.info("Add tweet:%s" % item["tweet_id"])

        elif isinstance(item, User):
            try:
                col = self._db["twitter_user"]
                col.insert_one(dict(item))
            except Exception as err:
                logger.debug(err)
            logger.info("Add user:%s" % item["user_id"])

        else:
            logger.debug("Item type is not recognized! type = %s" % type(item))


class SaveToFilePipeline(object):
    '' " pipeline that save data to disk " ''

    def __init__(self):
        settings = get_project_settings()

        self.saveTweetPath = settings["SAVE_TWEET_PATH"]
        self.saveUserPath = settings["SAVE_USER_PATH"]
        mkdirs(self.saveTweetPath)  # ensure the path exists
        mkdirs(self.saveUserPath)

    def process_item(self, item, spider):
        item["created_at"] = str(item["created_at"])

        if isinstance(item, Tweet):
            item["user"] = dict(item["user"])
            savePath = os.path.join(
                self.saveTweetPath,
                f"{item['tweet_id']}.json",
            )
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.info("skip tweet:%s"%item["id_"])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.info("Update tweet:%s"%item["id_"])
            else:
                self.save_to_file(item, savePath)
                logger.info("Add tweet:%s" % item["tweet_id"])

        elif isinstance(item, User):
            savePath = os.path.join(
                self.saveUserPath,
                f"{item['user_id']}.json",
            )
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.info("skip user:%s"%item["id_"])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.info("Update user:%s"%item["id_"])
            else:
                self.save_to_file(item, savePath)
                logger.info("Add user:%s" % item["user_id"])

        else:
            logger.debug("Item type is not recognized! type = %s" % type(item))

    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(dict(item), f, ensure_ascii=False)
