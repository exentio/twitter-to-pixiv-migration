import tweepy
import time, re, sys
from datetime import datetime
import argparse
import requests
import json, csv
from collections import namedtuple
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI, PixivError
from config import API_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKEN, TWITTER_USER_HANDLE, PIXIV_EMAIL, PIXIV_PASSWORD

sys.dont_write_bytecode = True

# Arguments
argparser = argparse.ArgumentParser(
  description='Twitter to Pixiv migration tool',
  usage='%(prog)s [options]',
  epilog='Code repo on: https://github.com/exentio/twitter-to-pixiv-migration')
argparser.add_argument('--csv',
  action='store_true',
  help='save Pixiv accounts and users without Pixiv in CSV files')
argparser.add_argument('--json',
  action='store_true',
  help='save Pixiv accounts and users without Pixiv in JSON files')
prog_args = argparser.parse_args()

# Storage for log files
follows_pixiv = []
follows_nopixiv = []
pixiv_follow = namedtuple(
  'pixiv_follow',
  ['twitter_handle','pixiv_id'])
no_pixiv_follow = namedtuple(
  'no_pixiv_follow',
  ['twitter_handle','twitter_bio','twitter_url'],
defaults=['','No bio.','No URL.'])

# Twitter auth
auth = tweepy.OAuthHandler(API_KEY, API_SECRET_KEY)
auth.set_access_token(ACCESS_TOKEN, SECRET_ACCESS_TOKEN)
twitter_api = tweepy.API(auth)

loop_count = 0
split_user_id = ''
print_str = ''

login_time = 0

# Retrieve follows
following_user_id_list = twitter_api.get_friend_ids(screen_name=TWITTER_USER_HANDLE)

for twitter_user_id in following_user_id_list:
  try:
    loop_count += 1
    twitter_id = twitter_api.get_user(user_id=twitter_user_id).screen_name
    user_profile = twitter_api.get_user(screen_name=twitter_id)
    profile_website_url = ''
    bio_real_urls = ''

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
        follows_pixiv.append(pixiv_follow(twitter_id, split_user_id))
        print_str = twitter_id + ' ID: ' + split_user_id

    if 'description' in user_profile.entities and split_user_id == '':
      # Get all urls in the profile bio
      profile_desc_urls = user_profile.entities['description']['urls']

      bio_real_urls = user_profile.description

      if profile_desc_urls:
        for desc_url in profile_desc_urls:
          real_url = desc_url['expanded_url']

        # Replace t.co URLs with real ones if requested
          if prog_args.json or prog_args.csv:
            tco_url = desc_url['url']
            bio_real_urls = bio_real_urls.replace(tco_url,real_url)

          if "pixiv" in real_url:
            # pixiv.me urls are handled separately
            if 'pixiv.me' in real_url:
              real_url = requests.get(real_url).url

            split_user_id = re.sub(r"\D", "", real_url)
            follows_pixiv.append(pixiv_follow(twitter_id, split_user_id))
            print_str = twitter_id + ' ID: ' + split_user_id
            if not prog_args.json or not prog_args.csv:
              break

    if split_user_id == '':
      print_str = twitter_id + ': no Pixiv link found.'

      follows_nopixiv.append(no_pixiv_follow(
        twitter_id,
        bio_real_urls,
        profile_website_url))

    print(str(loop_count) + '/' + str(len(following_user_id_list)) + '\t' + print_str)
    split_user_id = ''

  except tweepy.TweepyException as e:
    print(e)
    if isinstance(e, tweepy.TooManyRequests):
      print('Rate limit exceeded, code: 88 -> Retrying in 15 minutes')
      print(datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
      time.sleep(60 * 15)
    elif isinstance(e, tweepy.NotFound):
      print(twitter_id + ": user not found.")
    else:
      break

# Log generation
if follows_nopixiv:
  print("\nThe following Twitter accounts don't have a Pixiv link in their profile:")
  for nopixiv_user in follows_nopixiv:
    print(nopixiv_user.twitter_handle, end = ' ')

if prog_args.json or prog_args.csv:
  time_now = datetime.now()
  file_timestamp = time_now.strftime("%Y%m%d_%H%M%S")
  follows_pixiv_asdict = [item._asdict() for item in follows_pixiv]
  follows_nopixiv_asdict = [item._asdict() for item in follows_nopixiv]

if prog_args.json:
  with open(file_timestamp + '-pixiv.json', 'w', encoding='utf-8') as f:
    json.dump(follows_pixiv_asdict, f, ensure_ascii=False, indent=4)
  with open(file_timestamp + '-nopixiv.json', 'w', encoding='utf-8') as f:
    json.dump(follows_nopixiv_asdict, f, ensure_ascii=False, indent=4)

if prog_args.csv:
  with open(file_timestamp + '-pixiv.csv', 'w', encoding='utf-8') as f:
    csv_writer = csv.DictWriter(f, follows_pixiv[0]._asdict().keys())
    csv_writer.writeheader()
    csv_writer.writerows(follows_pixiv_asdict)
  with open(file_timestamp + '-nopixiv.csv', 'w', encoding='utf-8') as f:
    csv_writer = csv.DictWriter(f, follows_nopixiv[0]._asdict().keys())
    csv_writer.writeheader()
    csv_writer.writerows(follows_nopixiv_asdict)

# Pixiv following
g = GetPixivToken()
pixiv_api = AppPixivAPI()

print('\nPixiv following begin.')
print('This will take time, to avoid triggering Pixiv\'s rate limit.')
print('Due to the duration of a Pixiv session, the script may re-authenticate during the process.')

loop_count = 0

# Pixiv
for pixiv_follow in follows_pixiv:

  pixiv_id = pixiv_follow.pixiv_id

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
  print(str(loop_count) + '/' + str(len(follows_pixiv)) + '\t' + pixiv_id)

print("\nAll done!")