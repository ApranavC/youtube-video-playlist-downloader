import yt_dlp
import threading

class YouTubeDownloader:
    def __init__(self):
        self.progress_callbacks = {}

    def get_video_qualities(self, video_url):
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
            
            formats = info.get('formats', [])
            quality_options = {}

            for fmt in formats:
                height = fmt.get('height')
                if height and fmt.get('ext') == 'mp4':  # Filter only mp4 formats
                    quality_options[str(height)] = fmt['format_id']

            return sorted(quality_options.items(), key=lambda x: int(x[0]), reverse=True)  # Sort by resolution
        except Exception:
            return []


    def set_progress_callback(self, video_index, callback):
        """ Set callback function for each video's progress update """
        self.progress_callbacks[video_index] = callback

    def download_video(self, video_url, video_index, quality="720"):

        def progress_hook(d):
            if d['status'] == 'downloading':
                try:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes', 1)
                    percent = (downloaded / total) * 100 if total else 0
                    total_size = f"{total / (1024 * 1024):.2f} MB" if total else "Unknown"

                    progress_text = f"{percent:.2f}% of {total_size}"

                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index](progress_text)
                except Exception:
                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index]("Error parsing progress")

        # Get available qualities
        quality_options = self.get_video_qualities(video_url)
        selected_format_id = next((q[1] for q in quality_options if q[0] == quality), None)

        ydl_opts = {
            'format': selected_format_id if selected_format_id else 'best',
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
