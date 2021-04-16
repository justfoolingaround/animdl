AnimDL - Batch Downloader & Stream URL Fetcher
---

AnimDL is a reliable program to download all your anime(s) from a proper server.

Furthermore, this program contains various utilities that will be able to help you make a even greater client.

The batch downloader included in the program can be configured using the `config.env` file which also has an example `config.env.example` to help you configure your downloader.

Clickable Terminal URLs
---

There is a `FANCY_TERMINAL` key in the configuration file that grants you the ability to get clickable download url through the data displayed in the terminal. To view the terminals that support this, head [here.](https://gist.github.com/egmontkob/eb114294efbcd5adb1944c9f3cb5feda) 

If you use this attribute without using a supported terminal, your terminal's stdout will look very wacky and it's also a friendly reminder to use such better/feature-rich terminals. 

**On a quick note: cmd (Command Prompt) is not supported, don't use this attribute if you're using cmd.**

Requirements
---

- Python 3.9 +
- requests
- tqdm
- lxml.html

**Disclaimer**

Downloading copyrighted materials might be illegal in your country.

This uses AnimixPlay.To as the provider of stream urls and currently, only GogoAnime streams are supported. You can't really select the quality of the anime as it is the raw quality provided; the quality will fluctuate from 480p to 1080p.

You may edit or modify the code based on your need. You may recieve help from the developer in any sort of modification you're performing as long as it's not some edgy stuff.