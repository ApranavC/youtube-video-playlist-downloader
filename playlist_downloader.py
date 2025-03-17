import yt_dlp
import os

class YouTubeDownloader:
    def __init__(self):
        self.progress_callbacks = {}  
        self.playlist_name = None  

    def get_video_qualities(self, video_url):
        """Fetch available video qualities from YouTube."""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(video_url, download=False)
            
            formats = info.get('formats', [])
            quality_options = {}

            for fmt in formats:
                height = fmt.get('height')
                if height and fmt.get('ext') == 'mp4':  # Only select MP4 formats
                    quality_options[str(height)] = fmt['format_id']

            return sorted(quality_options.items(), key=lambda x: int(x[0]), reverse=True)  # Sort by resolution
        except Exception:
            return []

    def set_progress_callback(self, video_index, callback):
        """Assign a callback function to update progress for each video."""
        self.progress_callbacks[video_index] = callback

    def check_if_video_exists(self, video_title):
        """Check if a video file already exists in the download folder."""
        folder_output = self.playlist_name if self.playlist_name else 'Downloads'
        file_path_mp4 = os.path.join(folder_output, f"{video_title}.mp4")

        if os.path.exists(file_path_mp4):
            return file_path_mp4
        return None

    def download_video(self, video_url, video_index, quality="720", on_complete=None):
        """Download a single video from YouTube and track progress."""
        
        def progress_hook(d):
            """Update GUI with download progress."""
            if d['status'] == 'downloading':
                try:
                    downloaded = d.get('downloaded_bytes', 0)
                    total = d.get('total_bytes', 1)
                    percent = (downloaded / total) * 100 if total else 0
                    total_size = f"{total / (1024 * 1024):.2f} MB" if total else "Unknown"

                    progress_text = f"Downloading: {percent:.2f}% of {total_size}"

                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index](progress_text)
                except Exception:
                    if video_index in self.progress_callbacks:
                        self.progress_callbacks[video_index]("Error tracking progress")

            elif d['status'] == 'finished':
                if video_index in self.progress_callbacks:
                    self.progress_callbacks[video_index]("Download Completed ✔️")

                file_path = d.get('filename', '')
                if os.path.exists(file_path):
                    print(f"✅ Download successful: {file_path}")
                else:
                    print(f"❌ Download failed: {file_path}")

                if on_complete:
                    on_complete()

        # Get video information (title, available qualities)
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(video_url, download=False)
        
        video_title = info.get('title', 'Unknown Video')

        # **Check if the video is already downloaded**
        existing_file = self.check_if_video_exists(video_title)
        if existing_file:
            print(f"⚠️ Video already exists: {existing_file}")
            if video_index in self.progress_callbacks:
                self.progress_callbacks[video_index]("Already downloaded ✔️")
            if on_complete:
                on_complete()
            return  # **Skip re-downloading**

        # Get available qualities
        quality_options = self.get_video_qualities(video_url)
        selected_format_id = next((q[1] for q in quality_options if q[0] == quality), None)

        folder_output = self.playlist_name if self.playlist_name else 'Downloads'

        ydl_opts = {
            'format': f"{selected_format_id}+bestaudio/best" if selected_format_id else 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'outtmpl': f'{folder_output}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook],
            'noplaylist': True,
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

    def download_playlist(self, playlist_url, update_ui_callback):
        """Detect if the URL is a single video or a playlist and process accordingly."""
        ydl_opts = {'ignoreerrors': True}
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(playlist_url, download=False)

            if 'entries' not in info or info.get('_type') == 'video':
                print("🎥 Detected single video. Treating as a video, not a playlist.")
                self.playlist_name = "Downloads"
                update_ui_callback([{'title': info.get('title', 'Unknown Video'), 'url': playlist_url}])
                return

            self.playlist_name = info.get('title', 'Unknown_Playlist')

            videos = []
            for vid in info.get('entries', []):
                if vid is None:
                    print("Skipping private or unavailable video in playlist.")
                    continue
                
                video_url = vid.get('webpage_url')
                video_title = vid.get('title')

                if video_url and video_title:
                    videos.append({'title': video_title, 'url': video_url})
                else:
                    print("Skipping private or unavailable video in playlist.")

            if not videos:
                print("No valid videos found in playlist!")

            update_ui_callback(videos)
        except Exception as e:
            print(f"Error processing URL: {e}")
            update_ui_callback([])

    def start_playlist_download(self, videos):
        """Download all videos in a playlist sequentially."""
        def download_next(index):
            if index >= len(videos):
                print("✅ All videos downloaded successfully!")
                return

            video = videos[index]
            print(f"🎥 Downloading {video['title']}...")

            self.download_video(video['url'], index, "720", lambda: download_next(index + 1))

        download_next(0)
