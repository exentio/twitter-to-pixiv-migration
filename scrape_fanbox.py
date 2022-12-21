import requests
import time, sys
import math
import argparse
import csv, json
import re
import tldextract
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from gppt import GetPixivToken
from pixivpy3 import AppPixivAPI, PixivError
from config import PIXIV_EMAIL, PIXIV_PASSWORD

sys.dont_write_bytecode = True

login_time = 0
fanbox_urls = []
pixiv_tofollow = []
url_nopixiv = []
current_follows = []

# Arguments
argparser = argparse.ArgumentParser(
  description='Fanbox scraper for Pixiv IDs. Better suited for plain text files, or outputs from follow.py',
  usage='%(prog)s [options]',
  epilog='Code repo on: https://github.com/exentio/twitter-to-pixiv-migration')
arg_group = argparser.add_mutually_exclusive_group(required=True)
arg_group.add_argument('--text',
  help='scrape Fanbox URLs saved in a plain text file (one URL per line, no extra text)')
arg_group.add_argument('--csv',
  help='scrape Fanbox URLs saved in a CSV file (needs --key)')
arg_group.add_argument('--json',
  help='scrape Fanbox URLs saved in a JSON file (needs --key)')
argparser.add_argument('--key',
  action='append',
  help='column name (CSV) or key (JSON) with the Fanbox URLs, can be used multiple times. If using files from follow.py, use "twitter_bio" and/or "twitter_url"')
prog_args = argparser.parse_args()

if (prog_args.json or prog_args.csv) and not prog_args.key:
  sys.exit("Column name/key not specified (use --key).")

if prog_args.text and prog_args.key:
  print("--text flag used, --key will be ignored.")

if prog_args.csv:
  with open(prog_args.csv) as csv_file:
    csv_content = csv.reader(csv_file, delimiter=',')
    first_row = True
    relevant_columns = []

    for row in csv_content:

      if first_row:
        for index, value in enumerate(row):
          for key in prog_args.key:
            if value == key:
              relevant_columns.append(index)
              first_row = False
        if first_row:
          sys.exit("Key(s) not found.")

      else:
        for column in relevant_columns:
          # Sigh, the URL extracting process is a mess, so it needs many steps to clean it up
          row_url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', row[column])
          for url in row_url:
            if 'fanbox.cc' in url:
              final_url = 'https://' + tldextract.extract(url).subdomain + '.fanbox.cc'
              fanbox_urls.append(final_url)

if prog_args.json:
  with open(prog_args.json) as json_file:
    json_content = json.load(json_file)
    for value in json_content:
      for key in prog_args.key:
        row_url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', value[key])
        for url in row_url:
          if 'fanbox.cc' in url:
            final_url = 'https://' + tldextract.extract(url).subdomain + '.fanbox.cc'
            fanbox_urls.append(final_url)

if prog_args.text:
  with open(prog_args.text) as text_file:
    for line in text_file:
      if not line.startswith('http'):
        line = 'https://' + line
      fanbox_urls.append(line.rstrip())

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

for url in fanbox_urls:
  loop_count += 1
  id_found = False
  print(str(loop_count) + '/' + str(len(fanbox_urls)) + "\t" + url)
  driver.get(url)

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
    if 'pixiv' in link_href:
      pixiv_url = requests.get(link_href).url
      pixiv_id = re.sub(r"\D", "", pixiv_url)
      pixiv_tofollow.append(pixiv_id)
      id_found = True

  if not id_found:
    url_nopixiv.append(url)

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

print("\nCouldn't find a Pixiv link in the following Fanbox URLs:")
print(url_nopixiv)

print("\nAll done!")