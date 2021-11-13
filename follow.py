import tweepy
import datetime, time, re
from pixivpy3 import AppPixivAPI
from true_key import REFRESH_TOKEN, API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN

# login
pixiv_api = AppPixivAPI()
pixiv_api.auth(refresh_token=REFRESH_TOKEN)

auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)

twitter_api = tweepy.API(auth)
search_user = 'genshi_hobby'

following_user_num_id_list = twitter_api.friends_ids(search_user)
following_user_num_id_list_len = len(following_user_num_id_list)
loop_count = 0
split_user_id = ''
# pixivpyの使用上フォローできなかったユーザー
could_not_follow_user = []

for item in following_user_num_id_list:
  try:
    twitter_id = twitter_api.get_user(item).screen_name

    # プロフィール情報の処理
    user_profile = twitter_api.get_user(twitter_id)

    # プロフィールにwebsiteがある場合のみリストに追加
    if('url' in user_profile.entities):

      # website取得
      profile_website_url = user_profile.entities['url']['urls'][0]['expanded_url']

      loop_count += 1
      # print(str(loop_count) + '/' + str(following_user_num_id_list_len))
      if('pixiv' in profile_website_url):
        if((not ('pixiv.me' in profile_website_url))):
          split_user_id = re.sub(r"\D", "", profile_website_url)
          pixiv_api.user_follow_add(split_user_id)

        else:
          could_not_follow_user.append(twitter_id)
          print('追加できなかったUser ' + str(could_not_follow_user))


      print(str(loop_count) + '/' + str(following_user_num_id_list_len) + ' ' + twitter_id + ' ID:' + split_user_id)
      split_user_id = ''


  except tweepy.TweepError as e:
      print(e)
      if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
        print('Rate limit exceeded, code: 88 -> 15分停止')
        print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        time.sleep(60 * 15)

      else:
        break

print('pixivpyの仕様上フォローできなかったユーザー')
print(could_not_follow_user)
