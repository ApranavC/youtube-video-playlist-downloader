import tkinter as tk
from tkinter import ttk
import threading
from playlist_downloader import YouTubeDownloader

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Playlist Downloader")
        self.root.geometry("800x500")

        self.downloader = YouTubeDownloader()

        # 🎯 UI Components
        self.url_label = tk.Label(root, text="Enter Playlist URL:")
        self.url_label.pack(pady=5)

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.pack(pady=5)

        self.search_button = tk.Button(root, text="Search", command=self.search_videos)
        self.search_button.pack(pady=5)

        # 🎯 Video List Frame with Scrollbar
        self.video_frame = tk.Frame(root)
        self.video_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.video_frame)
        self.scrollbar = tk.Scrollbar(self.video_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.video_widgets = []

    def search_videos(self):
        """ Fetch playlist videos and display them in the UI """
        playlist_url = self.url_entry.get()
        if not playlist_url:
            return

        def update_ui(videos):
            """ Update UI with video list """
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()

            self.video_widgets.clear()

            for index, video in enumerate(videos):
                frame = tk.Frame(self.scrollable_frame, borderwidth=1, relief="solid", padx=5, pady=5)
                frame.pack(fill="x", pady=2)

                title_label = tk.Label(frame, text=video['title'], anchor="w")
                title_label.pack(side="left", padx=5, fill="x", expand=True)

                progress_label = tk.Label(frame, text="Not Started", width=25)
                progress_label.pack(side="left", padx=5)

                download_button = tk.Button(
                    frame, text="Download", 
                    command=lambda v=video, i=index, pl=progress_label: self.start_download(v, i, pl)
                )
                download_button.pack(side="right", padx=5)

                self.video_widgets.append({"progress": progress_label, "video": video, "button": download_button})

        threading.Thread(target=self.downloader.download_playlist, args=(playlist_url, update_ui)).start()

    def start_download(self, video, index, progress_label):
        """ Start downloading a video in a new thread """

        # 🔵 Update label to show "Starting..."
        progress_label.config(text="Starting...")

        def update_progress(progress_text):
            """ Update progress label for this video """
            progress_label.config(text=progress_text)

        def on_download_complete():
            """ Update label to show 'Completed' """
            progress_label.config(text="Completed")

        self.downloader.set_progress_callback(index, update_progress)

        # Start download in a thread
        thread = threading.Thread(target=self.run_download, args=(video['url'], index, on_download_complete))
        thread.start()

    def run_download(self, video_url, index, on_complete):
        """ Run the download process and update UI when done """
        self.downloader.download_video(video_url, index)
        self.root.after(100, on_complete)  # 🔵 Ensure UI updates after completion

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
