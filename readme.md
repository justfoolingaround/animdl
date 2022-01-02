<!-- ![AnimDL Cover](https://i.imgur.com/nNXSZi6.png) !-->

<p align="center"><img src="https://capsule-render.vercel.app/api?type=soft&fontColor=703ee5&text=justfoolingaround/animdl&height=150&fontSize=60&desc=Ridiculously%20efficient,%20fast%20and%20light-weight.&descAlignY=75&descAlign=60&color=00000000&animation=twinkling"></p>


<p align="center"><a href="https://github.com/justfoolingaround/animdl"><img src="https://forthebadge.com/images/badges/makes-people-smile.svg" height="30px"><img src="https://forthebadge.com/images/badges/made-with-python.svg" height="30px"><img src="https://forthebadge.com/images/badges/powered-by-black-magic.svg" height="30px"></a></p>
</h1>

<p align="center">
<a href="https://discord.gg/gaX2Snst2j">
<code>
<img src="https://img.shields.io/discord/925000668824080474.svg?color=%237289DA&label=Support%20Server&logo=Discord&style=for-the-badge" height="30px">
</code>
</a></p>


## Installation

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8320379373f743acb169e9fad94e5341)](https://app.codacy.com/gh/justfoolingaround/animdl?utm_source=github.com&utm_medium=referral&utm_content=justfoolingaround/animdl&utm_campaign=Badge_Grade_Settings)

Installation of [**animdl**](https://www.github.com/justfoolingaround/animdl) can be done using:

```sh

python -m pip install git+https://www.github.com/justfoolingaround/animdl

```

Note that you need to have git installed, else, you would need to download the repository and then, use:

```sh

python -m pip install .

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

- `mpv` can be installed using `brew install mpv`.

### Core features

- Abuses the developer's knowledge of internal streaming mechanisms in various different sites to hunt down high quality stream links.
- Doesn't make a single unnecessary request; the official site may make 1k requests, this tool makes 3~5.
- Doesn't use any heavy dependencies such as Selenium or Javascript Evaluators.
- Effectively bypasses DRMs in several streaming sites.
- Integrates powerful, fast and efficient internal HLS downloader.
- Only tool in existence to bypass [9Anime](https://9anime.to)'s cloudflare protection.
- Operates with full efficiency and speed by using Python's generator functions to their full capacity.
- Supports downloading with [Internet Download Manager](https://www.internetdownloadmanager.com/) optionally.
- Supports optional downloading with `ffmpeg` (see [Using ffmpeg](#using-ffmpeg)).
- Supports streaming with [`mpv`](https://github.com/mpv-player/mpv/), [`iina`](https://github.com/iina/iina) and [`vlc`](https://www.videolan.org/vlc/) (see [Streaming](#streaming))

### Usage

```
Usage: animdl [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  download  Download your favorite anime by query.
  grab      Stream the stream links to the stdout stream for external usage.
  schedule  Know which animes are going over the air when.
  search    Search for an anime in the provider.
  stream    Stream your favorite anime by query.
  test      Test the scrapability power.
```

**Examples:**

Streaming **One Piece**'s episode 1 on [**AnimePahe**](https://animepahe.com/) by placing a search forehand:

- ```
  animdl stream "one piece" -r 1
  ```

Streaming **One Piece**'s episode 1 on [**AnimeOut**](https://animepahe.com/) by placing a search forehand:

- ```
  animdl stream "animeout:one piece" -r 1
  ```

Streaming **One Piece**'s episode 1 on [**AnimeOut**](https://animepahe.com/) directly:

- ```
  animdl stream "https://www.animeout.xyz/download-one-piece-episodes-latest/" -r 1
  ```

**Downloading** and **grabbing** is the same as the examples, except the `download` and the `grab` command should be used.

**Note:** Downloading will take place in the working directory of this project!

### Range / `-r` option

`-r` is a command created to select ranges.

`1-10` will select from 1 to 10, `10-` will select everything after 10 and `-10` will select everything before 10.

Instead of `-`, `:` and `.` will also work.

**For example:**

`20 12 10-3 40-50`

will select episodes from 3 to 10 (inclusive), 12, 20 and from 40 to 50 (inclusive).

### Supported Sites

<!--Working: https://i.imgur.com/tG9nb8s.png, !Working: https://i.imgur.com/bTLO7LJ.png !-->

| Website                                      | Searcher Prefix      | Available Qualities | Status                                                                                     | Content Fetch Speed <br> (Per Episode) | Content Extension |
| -------------------------------------------- | -------------------- | ------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------- | ----------------- |
| [9Anime](https://9anime.to/)                 | `9anime`             | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/bTLO7LJ.png"></code></p> | <p align="center">3.27s</p>            | MP4 / TS          |
| [AllAnime](https://allanime.site/)           | `allanime`            | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4 / TS          |
| [AnimePahe](https://www.animepahe.com/)      | `animepahe`          | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">4.15s</p>            | MP4               |
| [AnimeOut](https://www.animeout.xyz/)        | `animeout`           | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MKV               |
| [Animixplay](https://www.animixplay.to/)     | `animixplay`         | 480p, 720p, 1080p   | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">4.17s</p>            | MP4 / TS          |
| [Animtime](https://animtime.com/)            | No searcher included | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4               |
| [Crunchyroll](https://www.crunchyroll.com/)  | `crunchyroll`        | All                 | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | TS                |
| [Kawaiifu](https://www.kawaiifu.com/) (NSFW) | `kawaiifu`           | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4               |
| [GogoAnime](https://www.gogoanime.pe/)       | `gogoanime`          | 480p, 720p, 1080p   | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">2.34s</p>            | MP4 / TS          |
| [Nyaa](https://nyaa.si/)       | `nyaa`      | All   | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>            | Torrent        |
| [Haho](https://www.haho.moe/) (NSFW)         | `haho`           | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4               |
| [Tenshi](https://www.tenshi.moe/)            | `tenshi`             | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4               |
| [Twist](https://www.twist.moe/)              | `twist`              | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4               |
| [Zoro](https://www.zoro.to/)                 | `zoro`   | 720p, 1080p         | <p align="center"><code><img height="20" src="https://i.imgur.com/tG9nb8s.png"></code></p> | <p align="center">0s</p>               | MP4 |

### More sites?

Currently, there are no plans to add more sites as **AnimDL** supports top sites that stream anime. However, this does not mean that this is it for the sites. You can raise as many issues as possible for requesting a new site.

**Note:** Your request may be denied in case of Cloudflare protections and powerful anti-bot scripts in the site.

### Streaming

Streaming will require either `mpv` or `vlc`. You will require these to be in your `PATH`, if not, simply make a `animdl_config.yml` on the working directory and add these configurations appropriately:

```yaml
players:
  mpv:
    executable: "mpv"
    opts: []
  vlc:
    executable: "vlc"
    opts: []
  iina:
    executable: "iina-cli"
    opts: []
```

### Using ffmpeg

`ffmpeg` can be used with animdl using the config file.

```yml
use_ffmpeg: true
```

This config will make the downloader use ffmpeg for HLS streams.

ffmpeg is set as optional because:

- It is ridiculously slow, the internal HLS downloader has higher speeds.
- It makes this project partially heavy-weighted.
- `stderr` stream reading for cases such as `mpd` when using tqdm did not work.

### Disclaimer

The disclaimer of this project can be found [here.](./disclaimer.md)

