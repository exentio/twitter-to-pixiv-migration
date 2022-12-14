import tweepy
import datetime, time, re
import sys
import requests
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI, PixivError
from config import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN, TWITTER_USER_HANDLE, PIXIV_EMAIL, PIXIV_PASSWORD

sys.dont_write_bytecode = True

# Twitter auth
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
twitter_api = tweepy.API(auth)

loop_count = 0
split_user_id = ''
follow_user_id_list = []
print_str = ''

# Retrieve follows
following_user_id_list = twitter_api.get_friend_ids(screen_name=TWITTER_USER_HANDLE)

for twitter_user_id in following_user_id_list:
  try:
    loop_count += 1
    twitter_id = twitter_api.get_user(user_id=twitter_user_id).screen_name
    user_profile = twitter_api.get_user(screen_name=twitter_id)

    # Add to list only if they have a website in their profile
    if('url' in user_profile.entities):

      # Get url
      profile_website_url = user_profile.entities['url']['urls'][0]['expanded_url']

      if 'pixiv' in profile_website_url:
        # pixiv.me urls are handled separately
        if ('pixiv.me' in profile_website_url):
          # pixiv.me redirects to the actual url with an ID, this gets that redirect
          profile_website_url = requests.get(profile_website_url).url

        split_user_id = re.sub(r"\D", "", profile_website_url)
        follow_user_id_list.append(split_user_id)
        print_str = twitter_id + ' ID: ' + split_user_id

      else:
        print_str = twitter_id + " has a non-Pixiv URL: " + profile_website_url

    else:
      print_str = twitter_id + ': no website found.'

    print(str(loop_count) + '/' + str(len(following_user_id_list)) + '\t' + print_str)
    split_user_id = ''

  except tweepy.TweepyException as e:
      print(e)
      if e.reason == "[{'message': 'Rate limit exceeded', 'code': 88}]":
        print('Rate limit exceeded, code: 88 -> Retrying in 15 minutes')
        print(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
        time.sleep(60 * 15)

      else:
        break

# Obtaining Pixiv token
print('Pixiv auth begin.')
g = GetPixivToken()

# Set your email address in "user" and your password in "pass_password
res = g.login(headless=True, user=PIXIV_EMAIL, pass_=PIXIV_PASSWORD)
refresh_token = res['refresh_token']

# Pixiv auth
pixiv_api = AppPixivAPI()

_e = None
for _ in range(3):
    try:
        pixiv_api.auth(refresh_token=refresh_token)
        break
    except PixivError as e:
        _e = e
        print(e)
        time.sleep(10)
else:  # failed 3 times
    raise _e
print('Pixiv auth done.')

# Pixiv following
loop_count = 0
print('Pixiv following begin.')
for pixiv_id in follow_user_id_list:

  # 10 second sleep to avoid congestion
  time.sleep(10)
  pixiv_api.user_follow_add(int(pixiv_id))
  loop_count += 1
  print(str(loop_count) + '/' + str(len(follow_user_id_list)) + ' ' + pixiv_id)

print("All done!")