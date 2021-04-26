AnimDL - Download & stream your favorite anime
---

AnimDL is a reliable program to download or stream all your favorite anime(s) with or without Fillers.

Furthermore, this program contains various utilities that will be able to help you make a even greater client.

Streaming with AnimDL
---

Streaming with AnimDL requires an additional dependency known as `mpv` which can be downloaded from [here](https://github.com/mpv-player/mpv/releases/). If you don't 
have `mpv` installed onto your PATH, the streaming mechanism will automatically be disabled and the downloading mechanism will be selected.

You can use AnimDL through the ['user-friendly' cli tool.](https://github.com/justfoolingaround/animdl/blob/master/cli.py)

It is recommended that you setup AnimeFillerList due to it being able to fetch appropriate episode name and filter fillers on your request.

The default cli does not support TwistMoe. TwistMoe can be used with the old cli tool though.

`cli_old.py` can be configured using the `config.env` file which also has an example `config.env.example` as a guideline.

The streaming client will be modified to an amazing AnimDL exclusive client *soon*.

**Disclaimer**

Downloading copyrighted materials might be illegal in your country.

**Additional Information**

This uses AnimixPlay and/or Twist.Moe as the provider of stream urls and in case of AnimixPlay, currently, only GogoAnime streams are supported. You can't really select the quality of the anime as it is the raw quality provided; the quality will fluctuate from 480p to 1080p in AnimixPlay and from 720p to 1080p in Twist.Moe.

You may edit or modify the code based on your need. You may recieve help from the developer in any sort of modification you're performing as long as it's not some edgy stuff.

Complete support for TwistMoe (using mechanism similar to [this](https://github.com/justfoolingaround/twistmoe-download-utils)) has been added.

Clickable terminal texts have been removed due to their false length that was expected to cause issue with tqdm.

**Developer Note:** Unless you're using a internet connection >250 Mbps, TwistMoe downloads will have massive fluctuations (downloads that are expected to happen in 2-3 minutes by tqdm could be held back to 2-3 times based on your internet speed). This is due to how the CDN processes the things; for now, there is no solution. 
Even in an unlikely use-case (assuming you're too rich to use these measly tools), like in >250 Mbps internet, download expected to happen in 10-20 seconds extended upto a minute. 
A concurrent/threaded mechanism also proved useless in this case due to same errors. 

If you are rate-limited during a download from twistcdn, you can simply re-run the downloader and it will try to continue from where it left.