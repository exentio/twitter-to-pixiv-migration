from pixivpy3 import AppPixivAPI
from key import REFRESH_TOKEN, USER_ID
from time import sleep
import json, os
# フォルダの作成

# login
api = AppPixivAPI()
api.auth(refresh_token=REFRESH_TOKEN)

api.user_follow_add(13868752)

print("ダウンロード終了")
