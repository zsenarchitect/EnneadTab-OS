
__title__ = "YoutubePlaylist"
__doc__ = "Checkout pre-recorded turtorials and demos about EnneadTab."

import webbrowser
from EnneadTab import LOG, ERROR_HANDLE


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def youtube_playlist():
    playlist = "https://youtube.com/playlist?list=PLz3VQzyVrU1iyoGV-kzWhCPsmh9cQWWoV"
    webbrowser.open_new(playlist)


if __name__ == "__main__":
    youtube_playlist()