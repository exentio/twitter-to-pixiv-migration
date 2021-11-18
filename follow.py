import tweepy
import datetime, time, re
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI
from key import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN

# twitterの認証
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
twitter_api = tweepy.API(auth)

search_user = 'ここに入れるユーザーのフォローユーザーのtwitterプロフィールからpixivアカウントを探す'
loop_count = 0
split_user_id = ''
follow_user_id_list = []
could_not_follow_user = []
print_str = ''

# フォローユーザーの取得
following_user_id_list = twitter_api.friends_ids(search_user)

for item in following_user_id_list:
  try:
    loop_count += 1
    twitter_id = twitter_api.get_user(item).screen_name
    user_profile = twitter_api.get_user(twitter_id)

    # プロフィールにwebsiteがある場合のみリストに追加
    if('url' in user_profile.entities):

      # website取得
      profile_website_url = user_profile.entities['url']['urls'][0]['expanded_url']

      # apiの仕様上pixiv.meのurlはuseridを取得できないため除外して別リストに保存
      if 'pixiv' in profile_website_url:
        if not ('pixiv.me' in profile_website_url):
          split_user_id = re.sub(r"\D", "", profile_website_url)
          follow_user_id_list.append(split_user_id)
          print_str = twitter_id + ' ID: ' + split_user_id

        else:
          could_not_follow_user.append(twitter_id)
          print_str = '追加できなかったUser: ' + twitter_id

      else:
        print_str = twitter_id

    else:
      print_str = 'Websiteなし: ' + twitter_id

    print(str(loop_count) + '/' + str(len(following_user_id_list)) + ' ' + print_str)
    split_user_id = ''

  except tweepy.TweepError as e:
      print(e)
      if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
        print('Rate limit exceeded, code: 88 -> 15分停止')
        print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        time.sleep(60 * 15)

      else:
        break

# pixivのrefresh_tokenの取得
g = GetPixivToken()

# userにメールアドレス, pass_パスワードを入れる
res = g.login(headless=True, user="ここにメールアドレスを入れる", pass_="ここにパスワードを入れる")
refresh_token = res['refresh_token']

# pixivの認証
pixiv_api = AppPixivAPI()
pixiv_api.auth(refresh_token=refresh_token)

# pixivのフォロー
loop_count = 0
print('フォローの開始')
for item in follow_user_id_list:

  # 僕の高専の寮の回線が遅いので1回ごとに10秒sleep
  time.sleep(10)
  pixiv_api.user_follow_add(item)
  loop_count += 1
  print(str(loop_count) + '/' + str(len(follow_user_id_list)) + ' ' + item)

print('pixivpyの仕様上フォローできなかったユーザー')
print(could_not_follow_user)
