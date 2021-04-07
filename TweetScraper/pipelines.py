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
        user = settings["MONGODB_USER"]
        passwd = settings["MONGODB_PASSWORD"]
        self._client = pymongo.MongoClient(
            f"mongodb://{user}:{passwd}@{host}:{port}/?authSource=admin")
        self._db = self._client[db]

    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            # if os.path.isfile(savePath):
            #     pass  # simply skip existing items
            #     # logger.debug("skip tweet:%s"%item["id_"])
            #     ### or you can rewrite the file, if you don't want to skip:
            #     # self.save_to_file(item,savePath)
            #     # logger.debug("Update tweet:%s"%item["id_"])
            # else:
            self.save_to_mongodb(item, "tweet")
            logger.debug("Add tweet:%s" % item["id_"])

        elif isinstance(item, User):
            # if os.path.isfile(savePath):
            #     pass  # simply skip existing items
            #     # logger.debug("skip user:%s"%item["id_"])
            #     ### or you can rewrite the file, if you don't want to skip:
            #     # self.save_to_file(item,savePath)
            #     # logger.debug("Update user:%s"%item["id_"])
            # else:
            self.save_to_mongodb(item, "user")
            logger.debug("Add user:%s" % item["id_"])

        else:
            logger.info("Item type is not recognized! type = %s" % type(item))

    def save_to_mongodb(self, item, item_type):
        item = dict(item)
        try:
            col = self._db[item_type]
            col.insert_one(item)

        except Exception as err:
            logger.info(err)


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
                # logger.debug("skip tweet:%s"%item["id_"])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update tweet:%s"%item["id_"])
            else:
                self.save_to_file(item, savePath)
                logger.debug("Add tweet:%s" % item["tweet_id"])

        elif isinstance(item, User):
            savePath = os.path.join(
                self.saveUserPath,
                f"{item['user_id']}.json",
            )
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.debug("skip user:%s"%item["id_"])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update user:%s"%item["id_"])
            else:
                self.save_to_file(item, savePath)
                logger.debug("Add user:%s" % item["user_id"])

        else:
            logger.info("Item type is not recognized! type = %s" % type(item))

    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname, "w", encoding="utf-8") as f:
            json.dump(dict(item), f, ensure_ascii=False)
