import tweepy
from pixivpy3 import AppPixivAPI
from true_key import REFRESH_TOKEN, API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN


# login
pixiv_api = AppPixivAPI()
pixiv_api.auth(refresh_token=REFRESH_TOKEN)

# twitterのフォローユーザーのprofile取得
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)

# 先ほど見た Access token と Access token secret を入力
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)

# API を作成
twitter_api = tweepy.API(auth)

# プロフィール情報を手に入れたい Twitter User ID
user_id = 'mery__S2_'

# ユーザー情報の取得
user = twitter_api.get_user(user_id)
# print(user)

print(user.entities['url']['urls'][0]['expanded_url'])

# api.user_follow_add(13868752)
