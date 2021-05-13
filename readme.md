
![AnimDL Cover](https://raw.githubusercontent.com/justfoolingaround/animdl/master/assets/cover.png)

AnimDL - Download & stream your favorite anime in best qualities
---

AnimDL is an incredibly powerful tool to download and/or stream your favorite anime alongside realtime upscaling. 

The core advantage of this tool is that, it can download and stream from the sites mentioned below without using inefficient dependencies like Selenium and JS Evaluators. 
This tool has taken advantage of internal streaming mechanisms in different site(s) such that, it acts as a browser itself internally to hunt down stream URL(s).

**IMPORTANT**

If you're using the `cli.py` file, the search query mechanism will only search through Animixplay unless you enter the url of a supported website.

For example:

| Query | Will Recognize | Action |
| ----- | -------------- | ------ |
| [`One Piece (AnimePahe Anime URL)`](https://animepahe.com/anime/b0c3ed18-0721-df22-574b-63dc56a57f68) | Yes | Will start scraping One Piece from AnimePahe |
| [`One Piece (AnimePahe Episode URL)`](https://animepahe.com/play/b0c3ed18-0721-df22-574b-63dc56a57f68/321b254b5d2f1349dc49b6db4f43ff028591e51c1b3ce7f51f23e1c2d0606961) | Yes | Will convert to anime URL and start scraping One Piece from it. This will not download a singular episode. |
| [`One Piece (Twist URL)`](https://twist.moe/a/one-piece) | Yes | Will start scraping One Piece from Twist |
| [`One Piece (Animixplay URL)`](https://animixplay.to/v1/one-piece) | Yes | Will start scraping One Piece from Animixplay |
| `one piece` | No | Will search through Animixplay and show selections |

The only way of interacting with something other than Animixplay URLs is to put the URL referencing to the providers mentioned below. 
This is done because:

- Searching through multiple sites is slow and inefficient.
- [Twist](https://www.twist.moe/) does not have a good search mechanism. (One Piece is not available but the above link will work.)
- [AnimePahe](https://www.animepahe.com/)'s search ajax cannot resolve Anime if the query string is less than 4 characters.

**Supported Site(s)**

| Website | Available Qualities | Status | Streamable | Downloadable |
| ------- | ------------------- | ------ | --------- | ------------ |
| [Animixplay](https://www.animixplay.to/) | Unknown  (Ranges from 360p to 1080p) | Working | Yes | Yes provided that the stream link is not m3u8. |
| [Twist](https://www.twist.moe/) | 720p, 1080p | Working | Yes | Yes | 
| [AnimePahe](https://www.animepahe.com/) | 360p, 480p, 720p, 1080p | Working | Yes | No |
| [4Anime](https://4anime.to/) | 360p, 480p, 720p, 1080p | Working | Yes | Yes |

**Coming soon (sites)**

- GogoAnime
- 9Anime (without using Selenium)

aaaaaand, just about everything that streams anime (just make a issue and I'll consider it)

**Coming soon (features)**

- HLS downloading; a support for downloading m3u8. There are libraries for this but they are not that efficient.
- GUI!?

**Streaming**

Streaming needs an additional dependency known as `mpv`, you can download it from [here.](https://github.com/mpv-player/mpv/releases/)

This dependency is incredibly efficient for streaming and light-weight too. You need to add it to your PATH for the tool to detect and run it.

**Shaders**

You can stream your favorite anime with realtime shaders from [bloc97/Anime4K](https://github.com/bloc97/Anime4K/). 
This means that you can upscale your anime to an incredibly high resolution. (A low quality 480p can be converted to 2160p). 

To use this feature, download your shaders to the working directory and make sure to configure shaders while using the "stream" feature. 
All you need to do is type down the shader name. To use multiple shaders, you may separate shaders using ';'.

For example: 

`Anime4K_Denoise_Bilateral_Mode.glsl;Anime4K_Upscale_CNN_M_x2_Deblur.glsl` can be passed as the shader argument given that both 
`Anime4K_Denoise_Bilateral_Mode.glsl` and `Anime4K_Upscale_CNN_M_x2_Deblur.glsl` are downloaded to the working directory from [here.](https://github.com/bloc97/Anime4K/releases/)

**Disclaimer**

Downloading or streaming copyrighted materials might be illegal in your country.