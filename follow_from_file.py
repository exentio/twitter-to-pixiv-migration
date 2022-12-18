import time, sys
import math
import argparse
import csv
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI, PixivError
from config import PIXIV_EMAIL, PIXIV_PASSWORD

sys.dont_write_bytecode = True

login_time = 0
pixiv_tofollow = []
current_follows = []

# Arguments
argparser = argparse.ArgumentParser(
  description='Pixiv follower. Better suited for plain text files, or outputs from follow.py',
  usage='%(prog)s [options]',
  epilog='Code repo on: https://github.com/exentio/twitter-to-pixiv-migration')
arg_group = argparser.add_mutually_exclusive_group(required=True)
arg_group.add_argument('--csv',
  help='follow Pixiv IDs saved in a CSV file (needs --key). If using files from follow.py, use "pixiv_id"')
argparser.add_argument('--key',
  help='column name (CSV) or key (JSON) with the Pixiv IDs.')
prog_args = argparser.parse_args()

if prog_args.csv and not prog_args.key:
  sys.exit("Column name/key not specified (use --key).")

if prog_args.csv:
  with open(prog_args.csv) as csv_file:
    csv_content = csv.reader(csv_file, delimiter=',')
    first_row = True
    relevant_column = 0

    for row in csv_content:

      if first_row:
        for index, value in enumerate(row):
          if value == prog_args.key:
            relevant_column = index
            first_row = False
            break
        if first_row:
          sys.exit("Key not found.")

      else:
        pixiv_tofollow.append(row[relevant_column])

# Pixiv
g = GetPixivToken()
pixiv_api = AppPixivAPI()

print('\nPixiv following begin.')
print('This will take time, to avoid triggering Pixiv\'s rate limit.')
print('Due to the duration of a Pixiv session, the script may re-authenticate during the process.')

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

# Filter follows to avoid unnecessary requests and waste less time
# This one was pure pain
user_details = pixiv_api.user_detail(res['user']['id'])
# User follows are given in pages with 30 entries each
pages = math.ceil((user_details['profile']['total_follow_users']) / 30)
for index in range(pages):
  raw_follows = pixiv_api.user_following(res['user']['id'], offset=(30 * index))
  for x in raw_follows['user_previews']:
    current_follows.append(str(x['user']['id']))
filtered_ids = [x for x in pixiv_tofollow if x not in current_follows]

# Pixiv following
loop_count = 0
if filtered_ids:
  for pixiv_id in filtered_ids:

    # Pixiv refresh tokens expire after 3600 seconds
    if ((time.time() - login_time) > 3200):
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
    print(str(loop_count) + '/' + str(len(filtered_ids)) + '\t' + pixiv_id)

else:
  print("No accounts to follow.")

print("\nAll done!")