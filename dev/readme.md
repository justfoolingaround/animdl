AnimDL for Developers
---

This part of the code is for developers who are and want to be associated with the codebase.

**Regular Expression**

These are all the regular expressions used internally in the program.

- [Animixplay](https://animixplay.to) Anime URL

```
^(?:https?://)?(?:\S+\.)?animixplay\.to/v\d+/([^?&/]+)
```

- [Twist](https://twist.moe) Anime URL

```
^(?:https?://)?(?:\S+\.)?twist\.moe/a/([^?&/]+)
```

- [AnimePahe](https://animepahe.com) Anime URL

```
^(?:https?://)?(?:\S+\.)?animepahe\.com/anime/([^?&/]+)
```

- [4Anime](https://4anime.to) Anime and/or Episode URL

```
^(?:https?://)?(?:\S+\.)?4anime\.to/(?:(?:anime/([^?&/]+))|(?:([^?&/]+)-episode-\d+))
```

- [GogoAnime](https://www1.gogoanime.ai) Anime and/or Episode URL

```
^(?:https?://)?(?:\S+\.)?gogoanime\.ai/(?:([^&?/]+)-episode-\d+|category/([^&?/]+))
```

**Writing a fetcher yourself**

You can modify the code for adding custom fetchers. These fetchers can produce any amount of stream links.

A fetcher function is a generator and needs to take 3 arguments: `session` (`requests.Session`), `url` (`str`) and a check. 
This check will take one integer argument. This check is for episode numbers, so apply it accordingly.

Your fetcher needs to provide a list with this structure:

```py
[
    {
        'quality': '1080',
        'stream_url': 'http://path/to/a/stream/url.mp4',
        'headers': {}, # These are download headers and must contain any authorization, cookies and/or referers if downloading the file requires so.
    },
    ...
]
```

Your fetcher must provide stream links in an consecutive (if there are no filler filters applied) ascending order for full accuracy.

**Future feature: HLS Downloading**

Currently, a HLS downloader is being considered for the project. `ffmpeg` is a valid consideration here, 
however, it will not be used for downloading (download progress will be difficult to measure). Atmost, 
it is expected to be used as a post processor (converting from `ts` to `mp4`).

If you can write a clean code that can do so, it might make it to the codebase.