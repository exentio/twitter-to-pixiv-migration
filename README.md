# Twitter to Pixiv migration tool

### WARNING: due to Elon Musk, the Twitter APIs might stop working at any moment.
### I'll eventually port the code to a scraper library that doesn't need API access.

### Requirements
* python3
* pip3
* python3-venv

For the Pixiv follows, you might also need to install Chromedriver, doesn't seem
necessary on Windows. On Linux, this step depends on your Linux distro. For Arch
Linux, you can install the `chromedriver` AUR package (or `chromedriver-beta` if
you use Google Chrome Beta).  
Should the script crash because of Selenium being missing, check [how to follow from log files](https://github.com/exentio/twitter-to-pixiv-migration#follow-from-file)

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

### Log output
You can optionally enable logs in JSON and/or CSV using the flags `--json` and
`--csv`. Both flags will generate two files, one for the accounts with a Pixiv
URL in their profile, and one for those who have none. The first will contain
their Twitter handle and their Pixiv ID, while the second will have their
Twitter handle, their bio, and the URL they set as their website.  
CSV is recommended as it can be opened with Excel or Google Sheets, but JSON
may be more readable with a simple text editor. You have the choice, you can
enable both at the same time.  

### Follow from file
This can be useful in case the following process got interrupted, or if you
have a list of Pixiv IDs for some reason. Launch the `follow_from_file.py`
script and specify the file you're using with `--text` for a plain text file,
 `--csv`, or `--json`; plain text files need to ONLY have one ID per line, no
extra text or symbols, while CSV and JSON files need the argument `--key` to
specify the field or key from which to get the values. When using the files
produced by `follow.py`, the key is `pixiv_id`.  

The JSON structure needs to be simple, as I can't implement an easy way to
cycle inside a complex JSON file from just command line arguments.  
Example of a JSON structure that has been tested (aka the output format of the
original script):
```json
[
    {
        "twitter_handle": "lalansane",
        "pixiv_id": "4007933"
    },
    ...
]
```

### Scraping IDs from Fanbox
Oh boy, this was A PAIN, and it'll eventually break. Anyway.  
Launch `scrape_fanbox.py` and feed it a JSON with `--json` or a CSV with
`--csv` specifying as many keys as needed with `--key` (type the arg once for
each key, like this `--key twitter_bio --key twitter_url`), or a plaintext file
that contains a Fanbox URL for each line. Selenium will scrape the page and the
script will then start following them automatically. It'll also bypass R18
popups, so **by using the script you state to be over 18 years old.**

# References
* https://github.com/upbit/pixivpy
* https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
* https://qiita.com/perlverity/items/a6bd388d96cb4ce69692
