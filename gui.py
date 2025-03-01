import tkinter as tk
from tkinter import ttk
import threading
from playlist_downloader import YouTubeDownloader
from tkinter import Menu
from tkinter.messagebox import showinfo
import webbrowser

class YouTubeDownloaderGUI:
    def aboutSoftware(self):
        print("This is a software that downloads youtube videos")
        showinfo("About", "This is a software that downloads youtube videos\nDeveloper: Psycho Coder")

    def openMoreSoftwares(self):
        webbrowser.open("https://github.com/itspsychocoder/")
        
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 TubeFetch - YouTube Downloader")
        self.root.geometry("850x550")
        self.root.configure(bg="#2C2F33")

        self.downloader = YouTubeDownloader()

        # 🔹 Title
        title_label = tk.Label(root, text="YouTube Playlist Downloader", font=("Arial", 18, "bold"), bg="#2C2F33", fg="white")
        title_label.pack(pady=10)

        # 🔹 Input Frame
        input_frame = tk.Frame(root, bg="#2C2F33")
        input_frame.pack(pady=5)

        self.url_entry = ttk.Entry(input_frame, width=55)
        self.url_entry.grid(row=0, column=0, padx=10, pady=5)

        self.search_button = ttk.Button(input_frame, text="🔍 Search", command=self.search_videos)
        self.search_button.grid(row=0, column=1, padx=5)

        mainMenu = Menu()

        fileMenu = Menu(mainMenu, tearoff=0)
        fileMenu.add_command(label="About Software", command=self.aboutSoftware)
        fileMenu.add_command(label="Visit Website", command=self.openMoreSoftwares)

        mainMenu.add_cascade(label="About", menu=fileMenu)
        root.config(menu=mainMenu)

        # 🔹 Video List Frame
        self.video_frame = tk.Frame(root, bg="#23272A", bd=2, relief="sunken")
        self.video_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.video_frame, bg="#23272A")
        self.scrollbar = ttk.Scrollbar(self.video_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#23272A")

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
                frame_color = "#424549" if index % 2 == 0 else "#36393F"
                frame = tk.Frame(self.scrollable_frame, bg=frame_color, padx=5, pady=5, relief="ridge", bd=2)
                frame.pack(fill="x", pady=2)

                title_label = tk.Label(frame, text=video['title'], anchor="w", bg=frame_color, fg="white", font=("Arial", 11, "bold"))
                title_label.pack(side="left", padx=5, fill="x", expand=True)

                progress_label = tk.Label(frame, text="⏳ Not Started", bg=frame_color, fg="white", width=25)
                progress_label.pack(side="left", padx=5)

                download_button = ttk.Button(
                    frame, text="⬇ Download", 
                    command=lambda v=video, i=index, pl=progress_label: self.start_download(v, i, pl)
                )
                download_button.pack(side="right", padx=5)

                self.video_widgets.append({"progress": progress_label, "video": video, "button": download_button})

        threading.Thread(target=self.downloader.download_playlist, args=(playlist_url, update_ui)).start()

    def start_download(self, video, index, progress_label):
        """ Start downloading a video in a new thread """

        # 🔵 Update label to show "Starting..."
        progress_label.config(text="🚀 Starting...")

        def update_progress(progress_text):
            """ Update progress label for this video """
            progress_label.config(text=f"📥 {progress_text}")

        def on_download_complete():
            """ Update label to show 'Completed' """
            progress_label.config(text="✅ Completed")

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
