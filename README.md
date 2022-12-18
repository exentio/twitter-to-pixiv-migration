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
**Disclaimer: as of now, plain text parsing is not implemented.**

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

# References
* https://github.com/upbit/pixivpy
* https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde
* https://qiita.com/perlverity/items/a6bd388d96cb4ce69692
