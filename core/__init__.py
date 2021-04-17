"""
Currently, the only scrapers in use is AnimixPlay.to and/or Twist.Moe + AnimeFillerList.

In the case of AnimixPlay.to, keep in mind that you wouldn't be able to select quality for your anime's episodes. (They will range from 480p to 1080p.)
In the case of Twist.Moe, you can pretty much expect quality ranging from 720p to 1080p.

The goal of the program is to provide you ad-free stream urls with an additional reliable batch downloader.

The stream urls being scraped are going to be from https://storage.googleapis.com/ or twist's CDN, so, the downloads and streams (twist.moe may not be streamable) are expected to be fast.
"""

from .classes import *
from .downloader.download import internal_download