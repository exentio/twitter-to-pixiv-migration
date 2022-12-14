# Twitter to Pixiv migration tool

### Requirements
* python3
* pip3
* python3-venv

For the Pixiv follows, you'll also need to install Chromedriver. This step
depends on your Linux distro. For Arch Linux, you can install the `chromedriver`
AUR package (or `chromedriver-beta` if you use Google Chrome Beta).

### Setup
```bash
$ git clone https://github.com/exentio/twitter-to-pixiv-migration.git
$ cd twitter-to-pixiv-migration
$ python3 -m venv venv
$ source venv/bin/activate # If you use fish, there's an activate.fish file too
$ (venv) pip install -r requirements.txt
```

#### Configuration
Create a config.py file with the following content and start adding your
keys and login details:

```python
API_KEY = "Insert your API key."
API_SECRET_KEY = "Insert your API secret Key"
ACCESS_TOKEN = "Insert your access token"
SECRET_ACCESS_TOKEN = "Insert your secret access token"
TWITTER_USER_HANDLE = "Insert your user handle without the @."
PIXIV_EMAIL = "Insert your Pixiv account's email."
PIXIV_PASSWORD = "Insert your Pixiv account's password."

```

A Twitter developer account is required, [get one here.](https://developer.twitter.com/en/portal/petition/essential/basic-info)
Create an application, get your app secrets, and set them as API_KEY,
API_SECRET_KEY, ACCESS_TOKEN, and SECRET_ACCESS_TOKEN.  

### Start migrating
To start the tool, simply start the script in a terminal.

```bash
$ cd twitter-to-pixiv-migration
$ source venv/bin/activate
$ python3 follow.py
```

# References
* https://github.com/upbit/pixivpy
* https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
* https://qiita.com/perlverity/items/a6bd388d96cb4ce69692
