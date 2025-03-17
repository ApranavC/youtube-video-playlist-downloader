import tkinter as tk
from tkinter import ttk, Menu
import threading
from playlist_downloader import YouTubeDownloader
from tkinter.messagebox import showinfo
import webbrowser

class YouTubeDownloaderGUI:
    def about_software(self):
        showinfo("About", "YouTube Playlist Downloader\nDeveloper: Your Name")

    def open_profile(self):
        webbrowser.open("https://your-profile-link.com")  # Replace with your profile

    def __init__(self, root):
        self.root = root
        self.root.title("TubeFetch - YouTube Downloader")
        self.root.geometry("900x600")
        self.root.configure(bg="#1E1E1E")  # Dark Theme

        self.downloader = YouTubeDownloader()

        # Title Bar
        title_frame = tk.Frame(root, bg="#252525", pady=10)
        title_frame.pack(fill=tk.X)
        title_label = tk.Label(title_frame, text="🎬 TubeFetch - YouTube Playlist Downloader",
                               font=("Arial", 18, "bold"), bg="#252525", fg="white")
        title_label.pack()

        # Input Frame
        input_frame = tk.Frame(root, bg="#1E1E1E")
        input_frame.pack(pady=15)

        tk.Label(input_frame, text="🔗 Enter YouTube URL:", bg="#1E1E1E", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=5)
        self.url_entry = ttk.Entry(input_frame, width=50)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)
        self.search_button = ttk.Button(input_frame, text="Search", command=self.search_videos)
        self.search_button.grid(row=0, column=2, padx=5)

        # Progress Label (Fixed)
        self.progress_label = tk.Label(root, text="Waiting for search...", bg="#1E1E1E", fg="yellow", font=("Arial", 12))
        self.progress_label.pack(pady=10)

        # Video List Table (Treeview)
        self.tree_frame = tk.Frame(root, bg="#1E1E1E")
        self.tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        columns = ("#", "Title", "Status")
        self.video_tree = ttk.Treeview(self.tree_frame, columns=columns, show="headings", height=10)
        self.video_tree.heading("#", text="#")
        self.video_tree.heading("Title", text="Video Title")
        self.video_tree.heading("Status", text="Status")

        self.video_tree.column("#", width=50, anchor=tk.CENTER)
        self.video_tree.column("Title", width=500, anchor=tk.W)
        self.video_tree.column("Status", width=150, anchor=tk.CENTER)

        self.video_tree.pack(fill=tk.BOTH, expand=True)

        # Log Box (For Real-time Updates)
        self.log_box = tk.Text(root, height=6, bg="black", fg="white", font=("Arial", 10))
        self.log_box.pack(pady=5, fill=tk.BOTH, expand=False)

        # Progress Bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, length=300, mode='determinate', variable=self.progress_var)
        self.progress_bar.pack(pady=5)

        # Download Button (Initially Disabled)
        self.download_button = ttk.Button(root, text="Download", command=self.start_download, state=tk.DISABLED)
        self.download_button.pack(pady=10)

        # Footer
        footer_label = tk.Label(root, text="© 2024 TubeFetch | Developed by Your Name",
                                bg="#1E1E1E", fg="gray", font=("Arial", 10, "italic"))
        footer_label.pack(side=tk.BOTTOM, pady=5)

    def log_message(self, message):
        """ Update the log box with new messages """
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.see(tk.END)

    def search_videos(self):
        """ Searches for videos and updates UI with real-time logs """
        playlist_url = self.url_entry.get()
        if not playlist_url:
            self.progress_label.config(text="⚠️ Please enter a YouTube URL!", fg="red")
            return

        self.progress_label.config(text="🔍 Searching...", fg="yellow")
        self.video_tree.delete(*self.video_tree.get_children())  # Clear previous search results
        self.progress_var.set(0)
        self.log_box.delete("1.0", tk.END)  # Clear logs

        def update_ui(videos):
            if not videos:
                self.progress_label.config(text="⚠️ No videos found!", fg="red")
                return

            self.videos = videos  # Store video data for download
            self.progress_label.config(text=f"✅ Found {len(videos)} video(s)", fg="green")

            for index, video in enumerate(videos, start=1):
                self.video_tree.insert("", "end", values=(index, video['title'], "Waiting"))
                self.log_message(f"📜 Found video {index}/{len(videos)}: {video['title']}")

            self.download_button.config(state=tk.NORMAL)  # Enable Download Button

        threading.Thread(target=self.downloader.download_playlist, args=(playlist_url, update_ui)).start()

    def start_download(self):
        """ Starts downloading videos and updates UI accordingly """
        self.progress_label.config(text="Starting download...", fg="yellow")
        self.progress_var.set(0)
        self.log_box.delete("1.0", tk.END)

        def update_progress(index, progress_text, progress_value):
            """ Updates UI with download progress """
            item_id = self.video_tree.get_children()[index]
            self.video_tree.item(item_id, values=(index + 1, self.videos[index]['title'], progress_text))

            self.progress_var.set(progress_value)
            self.log_message(f"⬇️ Downloading [{index+1}/{len(self.videos)}]: {self.videos[index]['title']} - {progress_text}")

        def on_complete():
            self.progress_label.config(text="✅ Download Completed!", fg="green")
            self.progress_var.set(100)
            self.log_message("✅ All downloads complete!")

        total_videos = len(self.videos)
        
        for index, video in enumerate(self.videos):
            self.downloader.set_progress_callback(index, lambda text, idx=index: update_progress(idx, text, (idx + 1) / total_videos * 100))

        threading.Thread(target=self.downloader.start_playlist_download, args=(self.videos,)).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
