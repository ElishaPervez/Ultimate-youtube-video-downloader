import os
import yt_dlp

class DownloaderLogic:
    def fetch_info(self, url):
        """
        Fetches video information without downloading.
        Returns the info dictionary.
        """
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return info

    def download(self, url, ydl_opts, progress_hook=None):
        """
        Downloads a video with the given options.
        """
        if progress_hook:
            ydl_opts['progress_hooks'] = [progress_hook]

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
