AnimDL - Batch Downloader & Stream URL Fetcher
---

AnimDL is a reliable program to download all your anime(s) from a proper server.

Furthermore, this program contains various utilities that will be able to help you make a even greater client.

The batch downloader included in the program can be configured using the `config.env` file which also has an example `config.env.example` to help you configure your downloader.

Requirements
---

- Python 3.8 +
- requests
- tqdm
- lxml.html

**Disclaimer**

Downloading copyrighted materials might be illegal in your country.

This uses AnimixPlay.To and/or Twist.Moe as the provider of stream urls and in case of AnimixPlay.To, currently, only GogoAnime streams are supported. You can't really select the quality of the anime as it is the raw quality provided; the quality will fluctuate from 480p to 1080p in AnimixPlay and from 720p to 1080p in Twist.Moe.

You may edit or modify the code based on your need. You may recieve help from the developer in any sort of modification you're performing as long as it's not some edgy stuff.

Complete support for TwistMoe (using mechanism similar to [this](https://github.com/justfoolingaround/twistmoe-download-utils)) has been added.

Clickable terminal texts have been removed due to their false length that was expected to cause issue with tqdm.