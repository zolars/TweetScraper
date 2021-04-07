from scrapy import Item, Field


class Tweet(Item):
    '''
    parameters:
        - source
        - created_at
        - collected_at
        - url
        - tweet_id
        - content
        - language
        - tweet_client
        - retweet_count
        - favorite_count
        - reply_count
        - quote_count
        - user
    '''
    created_at = Field()
    collected_at = Field()

    url = Field()
    tweet_id = Field()
    content = Field()
    language = Field()
    tweet_client = Field()

    retweet_count = Field()
    favorite_count = Field()
    reply_count = Field()
    quote_count = Field()

    in_reply_to_status_id = Field()
    in_reply_to_user_id = Field()

    user = Field()


class User(Item):
    '''
    parameters:
        - created_at
        - collected_at
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
    collected_at = Field()

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
