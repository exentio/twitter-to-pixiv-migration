# Twitter to Pixiv migration tool.

# Requirements
* python3
* pip3
* python3-venv

# Setup
```bash
$ git clone https://github.com/exentio/twitter-to-pixiv-migration.git
$ cd twitter-to-pixiv-migration
$ python3 -m venv venv
$ source venv/bin/activate # If you use fish, there's an activate.fish file too
$ (venv) pip install -r requirements.txt
$ sed -i 's/async/async_/g' venv/lib/python3.9/site-packages/tweepy/streaming.py
```
The change made by sed is unnecessary if you run Python 3.6 or lower, but if you run Python 3.7 or higher, it's needed due to `async` being changed into `async_`  -> [See this Tweepy issue](https://github.com/tweepy/tweepy/issues/1017)

## Setting the key.py
A Twitter developer account is required. Create an application, get your app secrets, and set them as API_KEY, API_SECRET_KEY, ACCESS_TOKEN, and SECRET_ACCESS_TOKEN in key.py.

```python
API_KEY = "Insert your API key."
API_SECRET_KEY = "Insert your API secret Key."
ACCESS_TOKEN = "Insert your access token."
SECRET_ACCESS_TOKEN = "Insert your secret access token."
```

## Start following
Enter the Twitter handle (without the @) of your account, or the one of which you want to migrate from, in the 12th line of follow.py (variable named `search_user`), your Pixiv email address and password in the 69th line (variable named `res`), and execute the following commands in the terminal.

```bash
$ cd twitter-to-pixiv-migration
$ python3 follow.py
```

Due to the current limitations of the pixivpy library, it's currently not possible to follow users who put a pixiv.me URL in their account.

# References
* https://github.com/upbit/pixivpy
* https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
* https://qiita.com/perlverity/items/a6bd388d96cb4ce69692
