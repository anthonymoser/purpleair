from config import twitter_config as tc
import tweepy


class PurpleTwitter:

    api = None
    last_tweet = None
    username = None
    default_img = None

    def __init__(self, default_img:str):
        self.username = tc.get('username', None)
        self.default_img = default_img if not None else 'aqi_levels.jpg'

        # Authenticate to Twitter
        auth = tweepy.OAuthHandler(tc['CONSUMER_KEY'], tc['CONSUMER_SECRET'])
        auth.set_access_token(tc['ACCESS_TOKEN'], tc['ACCESS_TOKEN_SECRET'])

        # Create API object
        self.api = tweepy.API(auth)

    def get_last_tweet(self):

        last_tweet = self.api.user_timeline(self.username, count=1)
        self.last_tweet = last_tweet[0].id
        return self.last_tweet

    def send_tweets(self, tweets:list, img:str = None, previous_tweet:str = None):

        if img is None:
            img = self.default_img

        for t in tweets:
            print(t)

            if previous_tweet:
                self.api.update_with_media(filename=img, status=t, in_reply_to_status_id=previous_tweet)
            else:
                self.api.update_with_media(filename=img, status=t)

            previous_tweet = self.get_last_tweet()


def split_tweets(intro: str, lines: list) -> list:
    # Splits updates into chunks of 260 characters or less
    tweets = []
    message = intro + " "

    for line in lines:
        if len(message + line) > 260:
            tweets.append(message)
            message = intro + line
        else:
            message += line

    tweets.append(message)
    return tweets