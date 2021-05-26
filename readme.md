
![AnimDL Cover](https://raw.githubusercontent.com/justfoolingaround/animdl/master/assets/cover.png)

# AnimDL - Download & Stream your favorite anime

**AnimDL** is an incredibly powerful tool for downloading and streaming anime.

### Core features

- Abuses the developer's knowledge of internal streaming mechanisms in various different sites to hunt down high quality stream links.
- Doesn't make a single unnecessary request to any servers and rules out such requests.
- Doesn't use any heavy dependencies such as Selenium or Javascript Evaluators.
- Effectively bypasses DRMs in several streaming sites.
- Integrates AnimeFillerList so that the user can filter out any fillers from downloading or streaming.
- Only tool in existence to bypass [9Anime](https://9anime.to)'s cloudflare protection.
- Operates with full efficiency and speed by using Python's generator functions to their full capacity.
- Supports streaming with [`mpv`](https://github.com/mpv-player/mpv/), an incredibly efficient, fast and light-weight dependency.

### Usage

```
animdl.py [( download | stream | grab ) --query QUERY | continue ]
```

Examples:

```py
animdl.py stream -q "one piece" -s 1 # Starts searching 'one piece' on 9Anime and streams from E01.
animdl.py stream -q "4anime:one piece" -s 1 # Starts searching 'one piece' on 4Anime and streams from E01.
animdl.py stream -q "https://9anime.to/watch/one-piece.ov8" -s 1 # Starts scraping One Piece from 9Anime and streams from E01.
```
Similarly, AnimeFillerList can be configured to get the episode names, filter out unwanted fillers and 
make animdl fully aware about when to stop (basically the end of the episodes).
```py
animdl.py stream -q "https://9anime.to/watch/one-piece.ov8" -s 1 -fl "https://animefillerlist.com/shows/one-piece" --fillers
```
The filler flag makes AnimDL skip through filler. It is recommened to use this AnimeFillerList integration when possible.

`4anime`, `9anime`, `animefreak`, `animepahe`, `animix`, `gogoanime`, `twist` (case insensitive) can be used as prefix followed by a ':' and the query to make AnimDL search from them.

You can quit AnimDL and continue watching anime from where you left it any time using the 'continue'.

Similarly, stream urls can be set to be printed / written on stdout using the 'grab' command.

### Installation

Clone / download the repository and simply run the following command in the working directory:

```
pip install -r requirements.txt
```

Python 3.6 >= is supported by AnimDL.

### Supported Sites

| Website | Available Qualities | Status | Streamable | Downloadable |
| ------- | ------------------- | ------ | --------- | ------------ |
| [4Anime](https://4anime.to/) | 720p, 1080p | Working | Yes | Yes |
| [9Anime](https://9anime.to/) | 720p, 1080p | Working | Yes | Yes for MP4, no for m3u8 |
| [AnimeFreak](https://www.animefreak.tv/) | 720p, 1080p | Working | Yes | Yes |
| [AnimePahe](https://www.animepahe.com/) | 720p, 1080p | Working | Yes | No |
| [Animixplay](https://www.animixplay.to/) | 480p, 720p, 1080p | Working | Yes | Yes for MP4, no for m3u8 |
| [GogoAnime](https://www1.gogoanime.ai/) | 480p, 720p, 1080p | Working | Yes | Yes for MP4, no for m3u8 |
| [Twist](https://www.twist.moe/) | 720p, 1080p | Working | Yes | Yes |

If a site is not working, please don't worry, you're encouraged to make an issue! 

Want more sites? AnimDL seems to support the best sites currently but that doesn't mean we won't add more sites! You're encouraged to raise as many issues as possible for requests to add support for an anime site.

### Streaming

Streaming needs an additional dependency known as `mpv`, you can download it from [here.](https://github.com/mpv-player/mpv/releases/)

If you're having issues with the installation of mpv, you can make an issue to recieve full help on its installation and usage.

### Coming soon (features)

- HLS downloading; a support for downloading m3u8. There are libraries for this but they are not that efficient.
- GUI (Possibly with Javascript frameworks, don't worry, I'll pick the most efficient one)

### Disclaimer

Downloading or streaming copyrighted materials might be illegal in your country. 