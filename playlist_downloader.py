import yt_dlp
import threading

class YouTubeDownloader:
    def __init__(self):
        self.progress_callbacks = {}
        self.playlist_name = None

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

        folder_output = self.playlist_name if self.playlist_name else 'Unknown_Playlist'

        ydl_opts = {
            'format': selected_format_id if selected_format_id else 'best',
            'merge_output_format': 'mp4',
            'outtmpl': f'Downloads/{folder_output}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])


    def start_sequential_download(self):
        self.download_sequence_button.config(state="disabled")  # Disable while downloading

        def download_next(index):
            if index >= len(self.video_widgets):  # Stop if all videos are done
                self.download_sequence_button.config(state="normal")  # Re-enable after completion
                return

            video_data = self.video_widgets[index]
            video = video_data["video"]
            progress_label = video_data["progress"]

            progress_label.config(text="Starting...")

            def update_progress(progress_text):
                progress_label.config(text=progress_text)

            def on_download_complete():
                progress_label.config(text="Completed")
                download_next(index + 1)  # Start the next video after completion

            self.downloader.set_progress_callback(index, update_progress)

            selected_quality = self.quality_var.get().replace("p", "")
            
            threading.Thread(target=self.run_download, args=(video['url'], index, selected_quality, on_download_complete)).start()

        download_next(0)  # Start from the first video

    def download_playlist(self, playlist_url, update_ui_callback):
        """ Fetch playlist details and update UI with video titles """

        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                playlist_name = playlist_info.get('title', 'Unknown_Playlist')  # Get playlist title
                self.playlist_name = playlist_name

            videos = [{'title': vid['title'], 'url': vid['webpage_url']} for vid in playlist_info.get('entries', [])]
            update_ui_callback(videos)
        except Exception:
            update_ui_callback([])
