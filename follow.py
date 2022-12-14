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
no_pixiv = []

login_time = 0

# Retrieve follows
following_user_id_list = twitter_api.get_friend_ids(screen_name=TWITTER_USER_HANDLE)

for twitter_user_id in following_user_id_list:
  try:
    loop_count += 1
    twitter_id = twitter_api.get_user(user_id=twitter_user_id).screen_name
    user_profile = twitter_api.get_user(screen_name=twitter_id)

    # Add to list only if they have a website in their profile
    if 'url' in user_profile.entities:
      # Get url
      profile_website_url = user_profile.entities['url']['urls'][0]['expanded_url']

      if 'pixiv' in profile_website_url:
        pixiv_url = profile_website_url
        # pixiv.me urls are handled separately
        if 'pixiv.me' in profile_website_url:
          # pixiv.me redirects to the actual url with an ID, this gets that redirect
          pixiv_url = requests.get(profile_website_url).url
        split_user_id = re.sub(r"\D", "", pixiv_url)
        follow_user_id_list.append(split_user_id)
        print_str = twitter_id + ' ID: ' + split_user_id

    if 'description' in user_profile.entities and split_user_id == '':
      # Get all urls in the profile bio
      profile_desc_urls = user_profile.entities['description']['urls']

      if profile_desc_urls:
        for tco_url in profile_desc_urls:
          real_url = tco_url['expanded_url']

          if "pixiv" in real_url:
            # pixiv.me urls are handled separately
            if 'pixiv.me' in real_url:
              real_url = requests.get(real_url).url

            split_user_id = re.sub(r"\D", "", real_url)
            follow_user_id_list.append(split_user_id)
            print_str = twitter_id + ' ID: ' + split_user_id
            break

    if split_user_id == '':
      print_str = twitter_id + ': no Pixiv link found.'
      no_pixiv.append(twitter_id)

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

# Pixiv following
g = GetPixivToken()
pixiv_api = AppPixivAPI()

print('\nPixiv following begin.')
print('This will take time, to avoid triggering Pixiv\'s rate limit.')
print('Due to the duration of a Pixiv session, the script may re-authenticate during the process.')

loop_count = 0

# Pixiv auth
for pixiv_id in follow_user_id_list:

  # Pixiv refresh tokens expire after 3600 seconds
  if (login_time == 0) or ((time.time() - login_time) > 3200):
    print('\nPixiv auth begin.')
    login_time = time.time()
    res = g.login(headless=True, user=PIXIV_EMAIL, pass_=PIXIV_PASSWORD)
    refresh_token = res['refresh_token']

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
    print('Pixiv auth done.\n')


  # 10 second sleep to avoid rate limit
  for remaining in range(10, 0, -1):
    sys.stdout.write("\r            \r")
    sys.stdout.write("Waiting {:d}.".format(remaining))
    sys.stdout.flush()
    time.sleep(1)

  pixiv_api.user_follow_add(int(pixiv_id))
  loop_count += 1

  sys.stdout.write("\r            \r")
  sys.stdout.flush()
  print(str(loop_count) + '/' + str(len(follow_user_id_list)) + '\t' + pixiv_id)

if no_pixiv:
  print("\nThe following Twitter accounts don't have a Pixiv link in their profile:")
  print(*no_pixiv)

print("\nAll done!")