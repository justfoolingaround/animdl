
![AnimDL Cover](https://raw.githubusercontent.com/justfoolingaround/animdl/master/assets/cover.png)

AnimDL - Download & stream your favorite anime
---

AnimDL is an incredibly powerful tool to download and/or stream your favorite anime. 

The core advantage of this tool is that, it can download and stream from the sites mentioned below without using inefficient dependencies like Selenium and JS Evaluators. 
This tool has taken advantage of internal streaming mechanisms in different site(s) such that, it acts as a browser itself internally to hunt down stream URL(s).

**Supported Site(s)**

| Website | Available Qualities | Status | Streamable | Downloadable |
| ------- | ------------------- | ------ | --------- | ------------ |
| [Animixplay](https://www.animixplay.to/) | Unknown  (Ranges from 360p to 1080p) | Working | Yes | Yes provided that the stream link is not m3u8. |
| [Twist](https://www.twist.moe/) | 720p, 1080p | Working | Yes (Slow) | Yes (Slow) | 
| [AnimePahe](https://www.animepahe.com/) | 360p, 480p, 720p, 1080p | Working | Yes (Ridiculously fast) | No |

**Coming soon (sites)**

- GogoAnime
- 9Anime (without using Selenium)
- 4Anime

aaaaaand, just about everything that streams anime (just make a issue and I'll consider it)

**Coming soon (features)**

- HLS downloading; a support for downloading m3u8. There are libraries for this but they are not that efficient.
- GUI!?

**Streaming**

Streaming needs an additional dependency known as `mpv`, you can download it from [here.](https://github.com/mpv-player/mpv/releases/)

This dependency is incredibly efficient for streaming and light-weight too. You need to add it to your PATH for the tool to detect and run it.

**Disclaimer**

Downloading copyrighted materials might be illegal in your country.