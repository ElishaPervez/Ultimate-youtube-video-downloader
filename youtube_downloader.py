import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import yt_dlp


class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        
        self.download_path = os.getcwd()
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        ttk.Label(main_frame, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        
        ttk.Label(main_frame, text="Download Path:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        path_frame.columnconfigure(0, weight=1)
        
        self.path_var = tk.StringVar(value=self.download_path)
        self.path_entry = ttk.Entry(path_frame, textvariable=self.path_var, state="readonly")
        self.path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.browse_button = ttk.Button(path_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=1, padx=(5, 0))
        
        self.download_button = ttk.Button(main_frame, text="Download", command=self.start_download)
        self.download_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W)
        
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_var.set(folder)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.progress_var.set(percent)
                self.status_var.set(f"Downloading... {percent:.1f}%")
            elif '_percent_str' in d:
                percent_str = d['_percent_str'].strip()
                self.status_var.set(f"Downloading... {percent_str}")
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.status_var.set("Download completed!")
            self.log_message(f"Downloaded: {d['filename']}")
            
    def download_video(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        try:
            self.download_button.config(state="disabled")
            self.progress_var.set(0)
            self.status_var.set("Starting download...")
            self.log_message(f"Starting download from: {url}")
            
            ydl_opts = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'format': 'best',
                'progress_hooks': [self.progress_hook],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            self.log_message("Download completed successfully!")
            messagebox.showinfo("Success", "Video downloaded successfully!")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_message(error_msg)
            self.status_var.set("Download failed")
            messagebox.showerror("Error", error_msg)
            
        finally:
            self.download_button.config(state="normal")
            self.progress_var.set(0)
            
    def start_download(self):
        thread = threading.Thread(target=self.download_video)
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()