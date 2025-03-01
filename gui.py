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

        self.quality_label = tk.Label(input_frame, text="Step 1: Enter Playlist URL")
        self.quality_label.grid(row=0, column=0, padx=10, pady=5)

        self.url_entry = ttk.Entry(input_frame, width=55)
        self.url_entry.grid(row=0, column=1, padx=10, pady=5)

        self.search_button = ttk.Button(input_frame, text="🔍 Search", command=self.search_videos)
        self.search_button.grid(row=0, column=2, padx=5)

        self.quality_label = tk.Label(input_frame, text="Step 2: Select Quality")
        self.quality_label.grid(row=1, column=0, padx=10, pady=5)

        self.quality_var = tk.StringVar()
        self.quality_dropdown = ttk.Combobox(input_frame, textvariable=self.quality_var, state="readonly")
        self.quality_dropdown.grid(row=1, column=1, padx=5, pady=5)

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

        self.signature_label = tk.Label(root, text="Made by: Psycho Coder", fg="gray", font=("Arial", 15, "italic"))
        self.signature_label.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)  # Bottom-right corner


    def search_videos(self):
        playlist_url = self.url_entry.get()
        if not playlist_url:
            return

        def update_ui(videos):
            if not videos:
                return

            # Get quality options for the first video
            quality_options = self.downloader.get_video_qualities(videos[0]['url'])
            if quality_options:
                self.quality_dropdown['values'] = [q[0] + "p" for q in quality_options]
                self.quality_var.set(self.quality_dropdown['values'][0])  # Set default

            # Populate videos in UI (existing logic)
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
        progress_label.config(text="Starting...")

        def update_progress(progress_text):
            progress_label.config(text=progress_text)

        def on_download_complete():
            progress_label.config(text="Completed")

        self.downloader.set_progress_callback(index, update_progress)

        # Get the selected quality
        selected_quality = self.quality_var.get().replace("p", "")
        
        thread = threading.Thread(target=self.run_download, args=(video['url'], index, selected_quality, on_download_complete))
        thread.start()


    def run_download(self, video_url, index, quality, on_complete):
        self.downloader.download_video(video_url, index, quality)
        self.root.after(100, on_complete)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderGUI(root)
    root.mainloop()
