# follow-pixiv-account-from-twitter-profile
指定したユーザーがフォローしているアカウントのTwitterプロフィールからpixivアカウントをフォローするやつ.

# Requirement
* python3
* pip3
* python3-venv

# Setup
```bash
$ git clone https://github.com/addtobasic/afollow-pixiv-account-from-twitter-profile.git
$ cd follow-pixiv-account-from-twitter-profile
$ python3 -m venv venv
$ source venv/bin/activate
$ (venv) pip install -r requirements.txt
$ sed -i 's/async/async_/g' venv/lib/python3.9/site-packages/tweepy/streaming.py
```
最後のsedコマンドによるパッケージの書き換えはpython3.6以下なら実行せずに動くが3.7以上の場合はasyncをasync_に書き換えなければならないため実行する必要があります -> [issuesを参照](https://github.com/tweepy/tweepy/issues/1017)

## Setting the key.py
面倒ですがtwitterのデベロッパーアカウントが必要です. 頑張って英作文ガチャに成功してください. アプリケーションを作りAPI_KEY, API_SECRET_KEY, ACCESS_TOKEN, SECRET_ACCESS_TOKENを書き換えてください.

```python
API_KEY = "Insert your API key."
API_SECRET_KEY = "Insert your API secret Key."
ACCESS_TOKEN = "Insert your access token."
SECRET_ACCESS_TOKEN = "Insert your secret access token."
```

## Start following
follow.pyの12行目に指定したユーザーのtwitterIDを, 69行目に自身のpixivのメールアドレスとパスワードを入力して, ターミナルで以下のコマンドを実行してください.

上記の設定が終わればターミナルで下のコマンドを実行してください
```bash
$ cd follow-pixiv-account-from-twitter-profile
$ python3 follow.py
```
これでsearch_userに設定したtwitterアカウントがフォローしているユーザーのtwitterプロフィールのwebsiteにあるpixivアカウントをフォローできていると思います.

pixivpyの仕様上, twitterに設定されたwebsiteがpixiv.meから始まるユーザーページだと直接フォローできないので最後にまとめて出力するようにしています

# References
* https://github.com/upbit/pixivpy
* https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
* https://qiita.com/perlverity/items/a6bd388d96cb4ce69692
