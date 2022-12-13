import tweepy
import datetime, time, re
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI
from key import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN

# Twitter auth
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
twitter_api = tweepy.API(auth)

search_user = 'Handle of the user without @'
loop_count = 0
split_user_id = ''
follow_user_id_list = []
could_not_follow_user = []
print_str = ''

# Retrieve follows
following_user_id_list = twitter_api.friends_ids(search_user)

for item in following_user_id_list:
  try:
    loop_count += 1
    twitter_id = twitter_api.get_user(item).screen_name
    user_profile = twitter_api.get_user(twitter_id)

    # Add to list only if they have a website in their profile
    if('url' in user_profile.entities):

      # Get url
      profile_website_url = user_profile.entities['url']['urls'][0]['expanded_url']

      # pixiv.me urls are handled separately
      if 'pixiv' in profile_website_url:
        if not ('pixiv.me' in profile_website_url):
          split_user_id = re.sub(r"\D", "", profile_website_url)
          follow_user_id_list.append(split_user_id)
          print_str = twitter_id + ' ID: ' + split_user_id

        else:
          could_not_follow_user.append(twitter_id)
          print_str = twitter_id + ' pixiv.me URL: ' + profile_website_url

      else:
        print_str = twitter_id

    else:
      print_str = 'No website found: ' + twitter_id

    print(str(loop_count) + '/' + str(len(following_user_id_list)) + ' ' + print_str)
    split_user_id = ''

  except tweepy.TweepError as e:
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
res = g.login(headless=True, user="Pixiv email", pass_="Pixiv password")
refresh_token = res['refresh_token']

# Pixiv auth
pixiv_api = AppPixivAPI()
pixiv_api.auth(refresh_token=refresh_token)
print('Pixiv auth done.')

# Pixiv following
loop_count = 0
print('Pixiv following begin.')
for item in follow_user_id_list:

  # 10 second sleep to avoid congestion
  time.sleep(10)
  pixiv_api.user_follow_add(item)
  loop_count += 1
  print(str(loop_count) + '/' + str(len(follow_user_id_list)) + ' ' + item)

print("Coudln't automatically follow these Twitter users:")
print(could_not_follow_user)
