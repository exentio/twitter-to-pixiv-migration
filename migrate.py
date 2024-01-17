import datetime, requests, re, sys, argparse, math, time
import ujson as json
from collections import namedtuple
from tweeterpy import TweeterPy
from tweeterpy import config
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI, PixivError

from config import TWITTER_AUTH_TOKEN, TWITTER_USER_HANDLE, PIXIV_EMAIL, PIXIV_PASSWORD

sys.dont_write_bytecode = True

# Arguments
arg_parser = argparse.ArgumentParser(
  description='Twitter to Pixiv migration tool',
  usage='%(prog)s [options]',
  epilog='Code repo on: https://github.com/exentio/twitter-to-pixiv-migration')

arg_group = arg_parser.add_mutually_exclusive_group()

arg_group.add_argument('--raw-json',
  type=argparse.FileType('r', encoding='UTF-8'),
  help='Restore from raw JSON account dumps created by this script or following the standard TweeterPy output.')
arg_group.add_argument('--urls-json',
  type=argparse.FileType('r', encoding='UTF-8'),
  help='Restore from JSON files containing parsed URLs created by this script or by hand.')
arg_parser.add_argument('--log',
  action='store_true',
  help='Log every Pixiv ID and lack thereof while parsing.')
prog_args = arg_parser.parse_args()

def datetime_handler(x):
  if isinstance(x, datetime.timedelta):
    return str(x)
  raise TypeError("Unknown type")

time_now = datetime.datetime.now()
file_timestamp = time_now.strftime("%Y%m%d_%H%M%S")

if not prog_args.raw_json and not prog_args.urls_json:
  twitter = TweeterPy()
  config.TIMEOUT = 10
  config.UPDATE_API = False
  twitter.generate_session(auth_token=TWITTER_AUTH_TOKEN)
  userid = twitter.get_user_id(TWITTER_USER_HANDLE)
  following_dump = twitter.get_friends(userid, follower=False, following=True, mutual_follower=False, end_cursor=None, total=None, pagination=True)["data"]

  with open('raw-following_' + file_timestamp + '.json', 'w', encoding="utf-8") as outfile:
    json.dump(following_dump, outfile, ensure_ascii=False, indent=4, default=datetime_handler)
elif prog_args.raw_json:
  following_dump = json.load(prog_args.raw_json)
elif prog_args.urls_json:
  following_dump = json.load(prog_args.urls_json)

follows_pixiv = []
# Accounts with URLs that can be scraped for Pixiv links
follows_fanbox = []
follows_potofu = []
follows_litlink = []
follows_linktree = []
follows_skeb = []
follows_booth = []
follows_foriio = []
# All URLs, including the above
follows_urls = []
follows_to_file = []

pixiv_id_follow = namedtuple(
  'pixiv_id_follow',
  ['twitter_handle','pixiv_id'])
single_url_follow = namedtuple(
  'url_follow',
  ['twitter_handle','url'])

def url_parsing(user_handle, user_urls, to_file=False):
  got_pixiv = False
  got_scrapeable = False
  pixiv_id = 0
  for single_url in user_urls:
    if 'pixiv' in single_url:
      pixiv_url = single_url
      # pixiv.me urls are handled separately
      if 'pixiv.me' in single_url:
        # pixiv.me redirects to the actual url with an ID, this gets that redirect
        pixiv_url = requests.get(single_url).url
      split_user_id = re.sub(r"\D", "", pixiv_url)
      # I once found a profile with an incomplete Pixiv URL, hence this
      if split_user_id:
        follows_pixiv.append(pixiv_id_follow(user_handle, split_user_id))
        got_pixiv = True
        pixiv_id = split_user_id
    else:
      if 'fanbox.cc' in single_url:
        follows_fanbox.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'potofu.me' in single_url:
        follows_potofu.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'lit.link' in single_url:
        follows_litlink.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'linktr.ee' in single_url:
        follows_linktree.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'skeb.jp' in single_url:
        follows_skeb.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'booth.pm' in single_url:
        follows_booth.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True
      elif 'fori.io' in single_url:
        follows_foriio.append(single_url_follow(user_handle, requests.get(single_url).url))
        got_scrapeable = True
      elif 'foriio.com' in single_url:
        follows_foriio.append(single_url_follow(user_handle, single_url))
        got_scrapeable = True

  if user_urls:
    follows_urls.append({
      "user_handle" : user_handle,
      "urls": user_urls
      })

  if to_file:
    follows_to_file.append({
      "user_handle" : user_handle,
      "display_name" : raw_data["legacy"]["name"],
      "user_bio" : raw_data["legacy"]["description"],
      "urls": user_urls
      })

  if prog_args.log:
    if got_pixiv:
      print(user_handle + " - Pixiv ID: " + pixiv_id + ".")
    elif got_scrapeable:
      print(user_handle + " - no Pixiv found, scrapeable sites found.")
    else:
      print(user_handle + " - no Pixiv found.")

if not prog_args.urls_json:
  for followed_acc in following_dump:
    if 'result' in followed_acc["content"]["itemContent"]["user_results"]:
      raw_data = followed_acc["content"]["itemContent"]["user_results"]["result"]
      user_handle = raw_data["legacy"]["screen_name"]
      user_urls = []
      if 'url' in raw_data["legacy"]["entities"]:
        user_urls.append(raw_data["legacy"]["entities"]["url"]["urls"][0]["expanded_url"])
      raw_urls = raw_data["legacy"]["entities"]["description"]["urls"]
      for desc_url in raw_urls:
        if 'expanded_url' in desc_url:
          user_urls.append(desc_url["expanded_url"])
      url_parsing(user_handle, user_urls, to_file=True)

  with open('following-urls_' + file_timestamp + '.json', 'w', encoding="utf-8") as outfile:
    json.dump(follows_to_file, outfile, ensure_ascii=False, indent=4, default=datetime_handler)

else:
  for followed_acc in following_dump:
    user_handle = followed_acc["user_handle"]
    user_urls = followed_acc["urls"]

    url_parsing(user_handle, user_urls)

# Fanbox scraping

name_xpath = '//*[@id="root"]/div[5]/div[1]/div/div[1]/div/div/div/div[2]/div/div[1]/h1/a'
links_xpath = '//*[@id="root"]/div[5]/div[1]/div/div[1]/div/div/div/div[2]/div/div[1]/div/a'
r18pop_xpath = '//*[@id="root"]/div[4]/div[2]/div/div/div/div[5]/button'

# Options for headless craping
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-browser-side-navigation")
options.add_argument('--proxy-server="direct://"')
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--start-maximized")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument('log-level=3')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

driver = webdriver.Chrome(
  service=Service(ChromeDriverManager().install()),
  options=options)

loop_count = 0
for user in follows_fanbox:
  loop_count += 1
  print(str(loop_count) + '/' + str(len(follows_fanbox)) + "\t" + user.url)
  driver.get(user.url)

  try:
    WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, name_xpath)))
  except TimeoutException:
    # High chances of a 18+ warning popup
    WebDriverWait(driver, 3).until(
      EC.presence_of_element_located((By.XPATH, r18pop_xpath)))
    driver.find_element(By.XPATH, r18pop_xpath).click()
    WebDriverWait(driver, 3).until(
      EC.presence_of_element_located((By.XPATH, name_xpath)))

  profile_links = driver.find_elements(By.XPATH, links_xpath)
  for link in profile_links:
    link_href = link.get_attribute('href')
    if 'pixiv' in link_href and not 'sketch' in link_href:
      pixiv_url = requests.get(link_href).url
      pixiv_id = re.sub(r"\D", "", pixiv_url)
      follows_pixiv.append(pixiv_id_follow(user.twitter_handle, pixiv_id))

# Pixiv
g = GetPixivToken()
pixiv_api = AppPixivAPI()

login_time = 0
current_follows = []

print('\nPixiv following begin.')
print('This will take time, to avoid triggering Pixiv\'s rate limit.')
print('Due to the duration of a Pixiv session, the script may re-authenticate during the process.')

print('\nPixiv auth begin.')
login_time = time.time()
res = g.login(headless=True, username=PIXIV_EMAIL, password=PIXIV_PASSWORD)
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
filtered_ids = [x.pixiv_id for x in follows_pixiv if x.pixiv_id not in current_follows]
# Remove duplicates
filtered_ids = list(set(filtered_ids))

# Pixiv following
loop_count = 0
for pixiv_id in filtered_ids:

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
  print(str(loop_count) + '/' + str(len(filtered_ids)) + '\t' + pixiv_id)

print("\nAll done!")
