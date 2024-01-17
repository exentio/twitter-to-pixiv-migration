# Twitter to Pixiv migration tool

### WARNING: the script relies on a scraper that might stop working at any moment.

### Requirements
* python3
* pip3
* python3-venv

For the Pixiv auto-following, you might also need to install Chromedriver,
doesn't seem necessary on Windows, and new Selenium versions download it
themselves but I've been having mixed results. On Linux, this step depends on
your Linux distro. For Arch Linux, you can install the `chromedriver` AUR
package (or `chromedriver-beta` if you use Google Chrome Beta).  

### Setup
```bash
$ git clone https://github.com/exentio/twitter-to-pixiv-migration.git
$ cd twitter-to-pixiv-migration
$ python3 -m venv venv
$ source venv/bin/activate # If you use fish, there's an activate.fish file too
$ (venv) pip install -r requirements.txt
```

#### Configuration
Create a `config.py` file with the following content and start adding your
keys and login details:

```python
TWITTER_AUTH_TOKEN = "Insert your auth token"
TWITTER_USER_HANDLE = "Insert your user handle (or the handle to scrape) without the @."
PIXIV_EMAIL = "Insert your Pixiv account's email."
PIXIV_PASSWORD = "Insert your Pixiv account's password."

```

To obtain a Twitter auth token, you need to open your browser's dev tools and
look for the cookie named `auth_token`.  
On Chrome, this is achieved by **pressing F12 > Application tab > Cookies >
https://twitter.com**, on Firefox the process is the same but instead of
**Application** you'll need to click on **Storage**.  

**⚠️ WARNING: THE USE OF A SCRAPER HAS A NON-ZERO CHANCE OF RESULTING IN A BAN,
SO IT'S SUGGESTED TO USE A DIFFERENT ACCOUNT FROM YOUR MAIN ONE.**
I wouldn't say the chances are high, but better to be safe than sorry.

### Start migrating
To start the tool, simply start the script in a terminal.

```bash
$ cd twitter-to-pixiv-migration
$ source venv/bin/activate
$ python3 migrate.py
```

Launching the script with no arguments makes a full JSON dump of your Twitter
followings, named `following-[timestamp].json`. You can then pass the `--raw-json <file>`
argument to work on that file, without needing to re-scrape your account,
although you'll need to do it to update the dump.  
From there, the script will process the large dump in a more lightweight one
that only contains the users' Twitter handles, display name, bio, and their
URLs, and dump in in a `following-urls-[timestamp].json` file, which you can
pass to the script with the `--urls-json <file>` argument, it should be faster
to parse. You can also make your own JSON file of the second type by respecting
this JSON structure:  
```json
[
    {
        "user_handle": "uniunimikan",
        "display_name": "✹🍊",
        "user_bio": "うにみかん | https:\/\/t.co\/3BrWESR5Ei",
        "urls": [
            "https:\/\/lit.link\/uniunimikan",
            "http:\/\/pixiv.me\/uniunimikan"
        ]
    },
    ...
]
```
Note: escaping is probably unnecessary, it worked for me with unescaped URLs,
but still suggested to be on the safe side. Nothing prevents you to exploit
this structure as needed.  

### Automatic scraping
As of now, the script already scrapes Fanbox links for Pixiv URLs. I'm also
planning to add scraping for the following websites:  
+ Potofu.me
+ Lit.link
+ Linktr.ee
+ Skeb.jp
+ Booth.pm
+ Fori.io/Foriio.com

The display name and bio are saved for other kinds of scraping, like emails or
fediverse handles. I'm particularly interested in the latter but I don't know
if I have the patience to implement it.