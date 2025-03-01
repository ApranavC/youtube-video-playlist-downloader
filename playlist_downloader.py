import yt_dlp
import threading

class YouTubeDownloader:
    def __init__(self):
        self.progress_callbacks = {}

    def set_progress_callback(self, video_index, callback):
        """ Set callback function for each video's progress update """
        self.progress_callbacks[video_index] = callback

    def download_video(self, video_url, video_index):
        """ Download a single video and update progress """

        def progress_hook(d):
            """ Extract progress details and update UI """
            if d['status'] == 'downloading':
                try:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes', 1)  # Prevent division by zero
                    percent = (downloaded / total) * 100 if total else 0
                    total_size = f"{total / (1024 * 1024):.2f} MB" if total else "Unknown"

                    progress_text = f"{percent:.2f}% of {total_size}"

                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index](progress_text)
                except Exception:
                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index]("Error parsing progress")

        ydl_opts = {
            'format': 'bv*[height=720]+ba/best[height=720]',
            'merge_output_format': 'mp4',
            'outtmpl': '%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    def download_playlist(self, playlist_url, update_ui_callback):
        """ Fetch playlist details and update UI with video titles """

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

            videos = [{'title': vid['title'], 'url': vid['webpage_url']} for vid in playlist_info.get('entries', [])]
            update_ui_callback(videos)
        except Exception:
            update_ui_callback([])
