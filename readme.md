<p align="center"><img src="https://capsule-render.vercel.app/api?type=soft&fontColor=703ee5&text=justfoolingaround/animdl&height=150&fontSize=60&desc=Ridiculously efficient, fast and light-weight.&descAlignY=75&descAlign=60&color=00000000&animation=twinkling"></p>
<p align="center"><sup>A highly efficient, powerful and fast anime scraper.</sup></p><hr>

https://user-images.githubusercontent.com/44473782/160827857-cc51d72c-a6e9-4d25-a9f2-e2badda0133c.mp4


## Overview

- [Installation](#installation)
    1. [PIP Installation](#installation)
    2. [Source Code Download](#installation)
- [Support](#support)
- [Usage](#usage)
    - [`stream` / `download` / `grab`](#stream--download--grab)
    - [`-r` / `--range`](#r----range-argument)
    - [`--auto` **and** `--index`](#auto-flag-and---index-argument)
    - [`-s` / `--special`](#s----special-argument)
    - [`-q` / `--quality`](#q----quality-argument)
    - [**More** usage](#conclusion)
- [Providers](#providers)
- [Configurations](#configurations)
    - [Setting up providers](#setting-up-providers)
    - [Quality selection](#quality-selection)
    - [Player selection](#player-selection)
    - [`ffmpeg` set-up](#ffmpeg-set-up)
    - [Discord Rich Presence set-up](#discord-rich-presence-set-up)
    - [`fzf` set-up](#fzf-set-up)
    - [Schedule set-up](#schedule-set-up)
- [Contributing to the project](#contributing-to-the-project)
- [Project Disclaimer](#project-disclaimer)
- [In a nutshell](#in-a-nutshell)
- [Code redistribution](#code-redistribution)
- [From the author](#from-the-author)
- [Honourable mentions](#honourable-mentions)
    - [Similar Projects](#similar-projects)
    - [Internal Dependencies](#internal-dependencies)
- [Sponsoring the project](#sponsoring-the-project)



## Installation

This project can be installed on to your device via different mechanisms, these mechanisms are listed below in the order of ease.

1. PIP Installs Packages **aka** PIP Installation 

    ```
    $ pip install animdl
    ```

2. Source Code Download

    ```
    $ git clone https://www.github.com/justfoolingaround/animdl
    ```

    Given that you have [`git`](https://git-scm.com/) installed, you can clone the repository from GitHub. If you do not have or want to deal with installation of [`git`](https://git-scm.com/), you can simply download the repository using [this link.](https://github.com/justfoolingaround/animdl/archive/refs/heads/master.zip)

    After the repository is downloaded and placed in an appropriate directory, you can, either use [`runner.py`](./runner.py) to use the project without installation **or** use [`setup.py`](./setup.py) to proceed with the installation.

    The former can be done via:

    ```py
    $ python runner.py
    ```

    The latter can be done via:

    ```py
    $ pip install .
    ```

    Both commands are to be executed from the directory where the repository is located.

**Additional information:** You **must** have Python installed **and** in PATH to use this project properly. Your Python executable may be `py` **or** `python` **or** `python3`. **Only Python 3.6 and higher versions are supported by the project.**


## Support

You can contact the developer directly via this [email](mailto:kr.justfoolingaround@gmail.com). However, the most recommended way is to head to the discord server.

<p align="center">
<a href="https://discord.gg/gaX2Snst2j">
<img src="https://invidget.switchblade.xyz/gaX2Snst2j">
</a>
</p>

If you run into issues or want to request a new feature, you are encouraged to make a GitHub issue, won't bite you, trust me.

## Usage

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

The `stream` option is disabled automatically if the project cannot find any of the supported streamers.


### `stream` / `download` / `grab`

These commands are the main set of command in the project. All of them scrape the target site, the only difference is how it is used. 

- The `stream` option tosses the stream url to a player so that you can seamlessly binge your anime.
    - Streaming supports Discord Rich Presence with `pypresence`.
- The `download` option downloads the anime to your local machine.
    - Downloading is done in the directory where you run the project.
    - `-d` flag can be used to specify a download folder as well.
    - [Internet Download Manager](https://internetdownloadmanager.com/) is supported and can be used via `--idm` flag. This downloader cannot download HLS streams.
    - The project cannot modify the content type. That means, videos in the `ts` format need to be converted to other formats externally post download. 
    - The downloading process cannot be controlled.
        - If download speed fluctuates, it is a server-side problem. The project cannot "fix" it.
        - If the download is slow, it is based on the server's upload speed. The project cannot "fix" it. **Speedtests are not reliable and their results will not correspond to the download speeds obtained through the project.**
    - The project utilises the fastest and the most straight-forward way to download, there is no further optimisation, period.


- The `grab` option simply streams the stream url to the stdout stream.
    - This is useful for external usage and testing.

```
$ animdl stream "One Piece" 
```

<p align="center">
<sub>
Providers can be specified by using provider prefix, <code>9anime:One Piece</code>, will use the 9Anime provider.
</sub></p>

<p align="center">
<sub>
You can specify direct urls to the provider; the project will automatically detect the provider and continue scraping. This method ignores searching.<sub></p>


### `-r` / `--range` argument

This argument is shared by **stream**, **download** and **grab**, it can be used to hand over custom ranges for selecting episodes.

- This argument constructs a check for the episodes, hence, will not throw error if the episode count does not meet the scraping count.
- This argument can be used in **reverse** order, the constructer will automatically fix the order.
- Range intersections will not cause issues.
- `1` will be treated as a singular range from 1 to 1.
- `1-2` will be treated as a range from 1 to 2.
- `1-2,230-340` will be treated as two different checks. The first check will be from `1` to `2`, the second from `230` to `340`.
- You can use any separators, the project will automatically parse your range string.


### `--auto` flag **and** `--index` argument

This argument is shared by **stream**, **download** and **grab**, it can be used to automatically select the search result. The default argument for index is `1`, that is, the first stream.

`--auto --index 2` will automatically select the second search result without prompt.

### `-s` / `--special` argument

This argument is shared by **stream** and **download**, it can be used to hand over the latest episode of the anime by using `-s latest`. Similarly, the latest 2 episodes can be selected via `latest-2`. 

This argument changes the **flow** of episodes. This means, this will not isolate the other streams but just bring forward the required episodes. If an anime has 10 episodes, the flow will be changed to `10, 1, 2, 3, 4, 5, 6, 7, 8, 9` if `latest` is in used.

- This argument is compatible with `-r`, you will get the last episode of the range.

### `-q` / `--quality` argument

This argument is incredibly powerful and can be used to select streams from their **attributes**.

- `1080` will select the stream with the resolution of 1080.
- `1080/worst` will do the above but will also select the worst quality stream if that stream is not available.
- `best[title]` will select the best stream that has the `title` attribute.
- `best[title=r'^DUB']` will select the stream with the `title` attribute that matches the regular expression. If `r` is not used, the expression will be treated as a literal string.
- The normal integers can be substituted with `best` and `worst` for special parsing.
- You need not mention the quality in the argument if you just want an attribute.

You can find out what attributes are available for each stream by using the `grab` command.

```json
[
  {
    "stream_url": "https://yqwym.vizcloud.digital/simple/EqPFI_kQBAro1HhYl67rC8UuoVwHubb7CkJ7rqk+wYMnU94US2El/br/list.m3u8#.mp4",
    "headers": {
      "referer": "https://vizcloud.digital/embed/83P7OX0N8PLE"
    }
  },
  {
    "stream_url": "https://yqwym.vidstream.pro/EqPVIPsMWl322yVezviuGdNz9wsVp_2ySFow5Od52MBlQ9QQG34s9aQ0yhbkTfyI+tzdG4991O3X4fVqACOikmeZRvMNGrBeQ5aivXxFIkYzNJElHAM1icyfowvCviiceQevRCxV9F7i7CIYt0hIz61716gsQxXskJ6eV4Gg4_OC/br/list.m3u8",
    "headers": {
      "referer": "https://vizcloud.digital/embed/83P7OX0N8PLE"
    }
  },
  {
    "stream_url": "https://yzqq.mcloud.to/12a3c523f910040ae8d4785897aeeb0bc52ea15c07b9b6fb0a427baea96ed0842f54d0184c6820e9f935c248a146eb8df28cc21a817ad2e8c0eefd680420a692659945f21618bd454698bcbf6e42394f3d4ee734180c3281ce9bb00fcaa2298e7913aa40036bbb0abaf07046a14442c2f32c9df66b1a/r/list.m3u8",
    "headers": {
      "referer": "https://mcloud.to/embed/k18xp6"
    }
  }
]
```

This is the prettified output of `animdl grab "9anime:one piece"`, and the stream has `headers` and `stream_url` attributes.

If you feel that a particular stream is fast enough for you, `-q [stream_url=r'.+mcloud\.to.+']`<sub>(or equivalent, this is just for testing)</sub> will select that stream.

### Conclusion

This project posses powerful commands and arguments to aid them, there are **many** arguments that aren't specified here but are available in the project. This is done because these commands are advanced usage commands which may just cause confusion. Feel free to ask about them.

## Providers


| Website                                      | Searcher Prefix      | Available Qualities | Status / Elapsed Time | Content Extension |
| :------------------------------------------: | :-----------------: | :-----------------:  | :----: | :-----------------: |
| [9Anime](https://9anime.to/)                 | `9anime`             | 720p, 1080p | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/nineanime.png">  | MP4 / TS  |
| [AllAnime](https://allanime.site/)           | `allanime`            | 720p, 1080p | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/allanime.png">  | MP4 / TS          |
| [AnimePahe](https://www.animepahe.com/)      | `animepahe`          | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/animepahe.png">  | MP4               |
| [AnimeOut](https://www.animeout.xyz/)        | `animeout`           | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/animeout.png">  | MKV               |
| [Animixplay](https://www.animixplay.to/)     | `animixplay`         | 480p, 720p, 1080p   | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/animixplay.png">  | MP4 / TS          |
| [Animtime](https://animtime.com/)            | No searcher included | 720p, 1080p         |  <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/animtime.png">   | MP4               |
| [Crunchyroll](https://www.crunchyroll.com/)  | `crunchyroll`        | All                 |  <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/crunchyroll.png">   | TS                |
| [Kawaiifu](https://www.kawaiifu.com/) (NSFW) | `kawaiifu`           | 720p, 1080p         |  <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/kawaiifu.png">   | MP4               |
| [GogoAnime](https://www.gogoanime.pe/)       | `gogoanime`          | 480p, 720p, 1080p   | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/gogoanime.png">  | MP4 / TS          |
| [Haho](https://www.haho.moe/) (NSFW)         | `haho`           | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/haho.png">  | MP4               |
| [Tenshi](https://www.tenshi.moe/)            | `tenshi`             | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/tenshi.png">  | MP4               |
| [Twist](https://www.twist.moe/)              | `twist`              | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/twist.png">  | MP4               |
| [Zoro](https://www.zoro.to/)                 | `zoro`   | 720p, 1080p         | <img height="25" src="https://github.com/justfoolingaround/animdl-provider-benchmarks/raw/master/api/providers/zoro.png">  | TS |

The images above are automatically updated every few hours, hence, please be aware that the developers already know what's broken.

Some providers may not work due to DDoS protection services. We try our best to fix what's fixable. There are plenty of alternatives even if one goes down in the project.

<p align="center"><b>The project contains providers that aren't mentioned here. This is intentional.</b></p>

## Configurations

Configuration files can be globally or locally be specified.

You can use the `ANIMDL_CONFIG` environment variable to specify a configuration file on a global level.

Else, a file with the name `animdl_config.yml` in the working directory will be used if available.

Futhermore, the configuration files can be globally placed at:
- Windows:
    - `%USERPROFILE%/.animdl/config.yml`
- Anything else:
    - `$HOME/.config/animdl/config.yml`

Only a singular configuration file in the above priority order is used, configurations aren't merged.

### Setting up providers

You can specify a default provider using the `default_provider` configuration option.

```yml
default_provider: animixplay
```

This project uses a standardised url **per** provider. This makes the project capable of using different **official** proxies of the same provider.

This can be specified via `site_urls` by using the following configuration.

```yml
site_urls:
    animixplay: https://www.animixplay.to/
```

### Quality selection

You can specify a default quality using the `quality_string` configuration option.

```yml
quality_string: best[subtitle]/best
```

### Player selection

You can specify a default player using the `default_player` configuration option.

```yml
default_player: mpv
```

You can change player attributes, such as, what the `executable` is and what `opts` are to be passed during the player call.

```yml
players:
    mpv:
        executable: mpv
        opts: []
```

If the executable is found, the player will be eligible for use.

Currently supported players are:
- [`mpv`](https://mpv.io/)
- [`vlc`](https://www.videolan.org/vlc/)
- [`iina`](https://iina.io/)
- [`celluloid`](https://celluloid-player.github.io)
- [`ffplay`](https://www.ffmpeg.org/ffplay.html)
- `android` (Android Player, only available **when** there aren't any headers for the stream)

### ffmpeg set-up

You can make the project force `ffmpeg` for HLS downloading (awfully slow) and merging subtitles for downloads when external subtitles are available.

```yml
ffmpeg:
    executable: ffmpeg
    hls_download: false
    submerge: true
```

### Discord Rich Presence set-up

This project supports RPC clients, this can be enabled **only** from the configuration. To use this, you must have `pypresence` installed via:

```
$ pip install pypresence
```

```yml
discord_presence: true
```


### fzf set-up

You can force the project search prompts to use [`fzf`](https://github.com/junegunn/fzf).

This is an incredibly powerful tool and can enchance the user experience by a lot. For obvious reasons, you need to have it installed and on PATH (can be configured to use an executable path as well).

```yml
fzf:
    executable: fzf
    opts: []
    state: false
```

Users can benefit by using `fzf` and `animdl stream twist:` as this allows them to browse the **entire** Twist library with a heavenly interface.

<p align="center">
<img src="https://media.discordapp.net/attachments/856404208445292545/972471580640804894/unknown.png"></p>

The above screenshot has `fzf`'s user theme configured.

### Schedule set-up

The project can be used to view the schedule of the upcoming anime for the week with the user cherished time and date formats.

```yml
schedule:
    site_url: https://graphql.anilist.co/ # DO NOT CHANGE UNLESS YOU KNOW WHAT YOU'RE DOING
    date_format: "%b. %d, %A"
    time_format: "%X"
```

Please refer to [Python `datetime.strftime` documentation](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior) for the available formats.

## Contributing to the project

It is **not** recommended for any average Python developers to engage with the project codebase as the mechanisms used are extremely high level and requires greater understanding of the codebase and Python in general.

If you wish to, you can contribute to the project by submitting a pull request.

The best way to contribute would be to suggest the developer a provider or a feature, more better if you can show a logic of how that can be done, you'll be mentioned and thanked!

## Project disclaimer

The disclaimer of the project can be found [here](./disclaimer.md).

## In a nutshell,

- Abuses the developer's braincells in scraping to give about the fastest and most efficient toolset.
- Brings about a highly powerful codebase which is just about appropriate for scraping.
- Does not use any heavy dependencies by default.
- Does not use `selenium` **or** JavaScript evaluators for scraping.
- Integrates powerful internal tools such as a HLS downloader.
- Is maintained, **heavily** as far as possible.

## Code redistribution

Feel free to do so and take references from the codebase. You need not give credit to the project or [justfoolingaround](https://github.com/justfoolingaround), however, please do a `blame` check and see if the contributor wants to be credited.

## From the author

I just maintain this project for my gratification. I'd love to hear from you about your projects and problems (even unrelated to the project), so feel free to contact [me](https://github.com/justfoolingaround).

I'm glad you're here!

## Honourable mentions

### Similar Projects

- Shell
    - [ani-cli](https://github.com/pystardust/ani-cli)
- Kotlin
    - [Cloudstream-3](https://github.com/Lagradost/cloudstream-3)
    - [Saikou](https://github.com/saikou-app/saikou)

These are actively maintained projects, each of which has its own unique features and functionality.

### Internal Dependencies

- Core
    - [encode/httpx](https://github.com/encode/httpx)
    - [Legrandin/pycryptodome](https://github.com/Legrandin/pycryptodome)
    - [pallets/click](https://github.com/pallets/click)
    - [tqdm/tqdm](https://github.com/tqdm/tqdm)
    - [lxml/lxml](https://github.com/lxml/lxml)
- Optional
    - [junegunn/fzf](https://github.com/junegunn/fzf)
    - [qwertyquerty/pypresence](https://github.com/qwertyquerty/pypresence)

The project would definitely not be complete or even in a working state if it weren't for these dependencies.

## Sponsoring the project

Usually sponsors means funding which consequently means money but for the project, it means stars. Feel free to star the project if you think it is worthy of one. Moreover, you can just talk, banter and argue with the developer as that way you'll be paying with your time.

<p align="center">
<code>
<a href="https://www.codacy.com/gh/justfoolingaround/animdl/dashboard">
<img src="https://app.codacy.com/project/badge/Grade/a3a66c513f6949fb9f4aeb5fd26db937">
</a>
</code>
</p>

<p align="center">
<sup>You are an absolute legend, keep being awesome!</sup>
</p>