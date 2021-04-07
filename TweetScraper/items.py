from scrapy import Item, Field


class Tweet(Item):
    '''
    parameters:
        - source
        - created_at
        - url
        - tweet_id
        - content
        - language
        - tweet_client
        - user
    '''
    source = "twitter"

    created_at = Field()

    url = Field()
    tweet_id = Field()
    content = Field()
    language = Field()
    tweet_client = Field()

    user = Field()


class User(Item):
    '''
    parameters:
        - created_at
        - user_id
        - user_profile_url
        - user_name
        - user_screen_name
        - user_bio
        - user_followers
        - user_following
        - user_listed
        - country
        - state
        - city
    '''
    created_at = Field()

    user_id = Field()
    user_profile_url = Field()
    user_name = Field()
    user_screen_name = Field()
    user_bio = Field()
    user_followers = Field()
    user_following = Field()
    user_listed = Field()

    country = Field()
    state = Field()
    city = Field()
