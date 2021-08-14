
![AnimDL Cover](https://i.imgur.com/nNXSZi6.png)

<h1><p align="center"> AnimDL - Download & Stream Your Favorite Anime </p>

<p align="center"><a href="https://github.com/justfoolingaround/animdl"><img src="https://forthebadge.com/images/badges/makes-people-smile.svg" height="30px"><img src="https://forthebadge.com/images/badges/made-with-python.svg" height="30px"><img src="https://forthebadge.com/images/badges/powered-by-black-magic.svg" height="30px"></a></p>
</h1>

## Installation

Installation of [**animdl**](https://www.github.com/justfoolingaround/animdl) can be done using:

```sh

py -m pip install git+https://www.github.com/justfoolingaround/animdl

```

Note that you need to have git installed, else, you would need to download the repository and then, use:

```sh

py -m pip install .

```

**Support:** Python 3.6 and higher

### Installing [`mpv`](https://github.com/mpv-player/mpv/)

#### Windows:
- The easiest way to install mpv is by using [chocolatey](https://chocolatey.org/) package manager, it's an amazing tool can that be installed by following their [official documentation](https://chocolatey.org/install).
- After chocolatey is installed, `mpv` can be installed through a console window (For example: cmd) with an **admininstrator** priviledge by the command: `choco install mpv`.

#### Linux:
- For users using a Debian-based distro, `mpv` can be installed using `sudo apt install mpv`. 
- For users using an Arch-based distro, `mpv` can be installed using `sudo pacman -S mpv`.

#### Mac:
-  `mpv` can be installed using `brew install mpv`.

### Core features

- Abuses the developer's knowledge of internal streaming mechanisms in various different sites to hunt down high quality stream links.
- Doesn't make a single unnecessary request; the official site may make 1k requests, this tool makes 3~5.
- Doesn't use any heavy dependencies such as Selenium or Javascript Evaluators.
- Effectively bypasses DRMs in several streaming sites.
- Integrates AnimeFillerList so that the user can filter out any fillers from downloading or streaming.
- Integrates powerful, fast and efficient internal HLS downloader.
- Only tool in existence to bypass [9Anime](https://9anime.to)'s cloudflare protection.
- Operates with full efficiency and speed by using Python's generator functions to their full capacity.
- Supports downloading with [Internet Download Manager](https://www.internetdownloadmanager.com/) optionally.
- Supports streaming with [`mpv`](https://github.com/mpv-player/mpv/), an incredibly efficient, fast and light-weight dependency.
- Supports streaming with [`vlc`](https://www.videolan.org/vlc/), which might require some configurations to make it work.

### Usage

```
animdl.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.       

Commands:
  continue  Continue your downloads or stream from where t'was left.
  download  Download your favorite anime by query.
  grab      Stream the stream links to the stdout stream for external usage.
  schedule  Know which animes are going over the air when.
  stream    Stream your favorite anime by query.
```

**Examples:**

1. Streaming **One Piece** on [**9Anime**](https://9anime.to/) from episode 1 by placing a search forehand:

-
    ```
    animdl.py stream "one piece" -s 1
    ```


2. Streaming **One Piece** on [**AnimeOut**](https://animeout.xyz/) from episode 1 by placing a search forehand.

-
    ```
    animdl.py stream "animeout:one piece" -s 1
    ```

3. Streaming **One Piece** on [**9Anime**](https://9anime.to/) with anime url from episode 1.

-
    ```
    animdl.py stream "https://9anime.to/watch/one-piece.ov8" -s 1
    ```

4. Streaming with the setting of **3** with **AnimeFillerList** integration that filters out fillers.

- 
    ```
    animdl.py stream "https://9anime.to/watch/one-piece.ov8" -s 1 -fl "https://animefillerlist.com/shows/one-piece" --fillers
    ```
    
5. Continuing a previous stream / download session without worrying about the command.

- 
    ```
    animdl.py continue
    ```

6. Scraping the episode stream links of **One Piece** from **[9Anime](https://9anime.to/)** to **stdout** without downloading:

- 
    ```
    animdl.py grab "https://9anime.to/watch/one-piece.ov8" -s 1
    ```

**Downloading** is the same as the examples 1-4, except the `download` command is used.

### Supported Sites

<!--Working: https://i.imgur.com/tG9nb8s.png, !Working: https://i.imgur.com/bTLO7LJ.png !-->

| Website | Searcher Prefix | Available Qualities | Status | Content Fetch Speed <br> (Per Episode) | Content Extension |
| ------- | ---------------- | ------------------- | ------ | ------------------ | ----------------- |
| [9Anime](https://9anime.to/) | `9anime` | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/bTLO7LJ.png"></code></p> | <p align="center">3.27s</p>   | MP4 / TS  | 
| [AnimePahe](https://www.animepahe.com/) | `animepahe` | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">4.15s</p>  | MP4 | 
| [AnimeOut](https://www.animeout.xyz/) | `animeout` | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>  | MKV | 
| [Animixplay](https://www.animixplay.to/) | `animixplay` | 480p, 720p, 1080p | <p align="center"><a href="javascript:alert('Cloudflare; unlikely to get fixed!')"><code><img height="20" src="https://i.imgur.com/bTLO7LJ.png"></code></a></p> | <p align="center">4.17s</p>  | MP4 / TS |
| [Animtime](https://animtime.com/) | No searcher included | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>  | MP4 |
| [GogoAnime](https://www.gogoanime.pe/) | `gogoanime` | 480p, 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">2.34s</p>   | MP4 / TS |
| [Tenshi](https://www.tenshi.moe/) | `tenshi` | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p> | MP4 |
| [Twist](https://www.twist.moe/) | `twist` | 720p, 1080p | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p> | MP4 |

### More sites?

Currently, there are no plans to add more sites as **AnimDL** supports top sites that stream anime. However, this does not mean that this is it for the sites. You can raise as many issues as possible for requesting a new site.

**Note:** Your request may be denied in case of Cloudflare protections and powerful anti-bot scripts in the site.

### Streaming

Streaming will require either `mpv` or `vlc`. You will require these to be in your `PATH`, if not, simply make a `animdl_config.json` on the working directory and add these configurations appropriately:

```json
{
    "players": {
            "vlc": {
                "executable": "<path-to-vlc>",
            },
            "mpv": {
                "executable": "<path-to-mpv>",
                "opts": [],
        },   
    }
}
```

### Disclaimer

Downloading or streaming copyrighted materials might be illegal in your country.
