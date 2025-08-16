import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from .downloader import VideoDownloader
from .utils import validate_youtube_url, get_default_download_path, format_duration, format_bytes

class YouTubeDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        self.downloader = VideoDownloader()
        self.video_info = None
        self.available_qualities = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        self.create_url_section(main_frame)
        self.create_quality_section(main_frame)
        self.create_output_section(main_frame)
        self.create_download_section(main_frame)
        self.create_progress_section(main_frame)
        self.create_info_section(main_frame)
        
        self.reset_ui()
    
    def create_url_section(self, parent):
        """Create URL input section."""
        ttk.Label(parent, text="YouTube URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        url_frame = ttk.Frame(parent)
        url_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=("TkDefaultFont", 9))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.fetch_btn = ttk.Button(url_frame, text="Fetch Info", command=self.fetch_video_info)
        self.fetch_btn.grid(row=0, column=1)
        
        self.url_entry.bind('<Return>', lambda e: self.fetch_video_info())
    
    def create_quality_section(self, parent):
        """Create quality selection section."""
        ttk.Label(parent, text="Quality:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(parent, textvariable=self.quality_var, state="readonly", width=20)
        self.quality_combo.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
    
    def create_output_section(self, parent):
        """Create output directory selection section."""
        ttk.Label(parent, text="Save to:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        output_frame = ttk.Frame(parent)
        output_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_var = tk.StringVar(value=get_default_download_path())
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_var)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.browse_btn = ttk.Button(output_frame, text="Browse...", command=self.browse_output_directory)
        self.browse_btn.grid(row=0, column=1)
    
    def create_download_section(self, parent):
        """Create download button section."""
        self.download_btn = ttk.Button(parent, text="Download Video", command=self.start_download)
        self.download_btn.grid(row=6, column=0, columnspan=2, pady=(0, 10))
    
    def create_progress_section(self, parent):
        """Create progress tracking section."""
        ttk.Label(parent, text="Progress:").grid(row=7, column=0, sticky=tk.W, pady=(0, 5))
        
        progress_frame = ttk.Frame(parent)
        progress_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.grid(row=0, column=1)
        
        self.status_var = tk.StringVar(value="Ready to download...")
        self.status_label = ttk.Label(parent, textvariable=self.status_var)
        self.status_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
    
    def create_info_section(self, parent):
        """Create video information display section."""
        info_frame = ttk.LabelFrame(parent, text="Video Information", padding="10")
        info_frame.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        ttk.Label(info_frame, text="Title:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.title_var = tk.StringVar(value="No video loaded")
        self.title_label = ttk.Label(info_frame, textvariable=self.title_var, wraplength=400)
        self.title_label.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(info_frame, text="Duration:").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.duration_var = tk.StringVar(value="--:--")
        ttk.Label(info_frame, textvariable=self.duration_var).grid(row=1, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Label(info_frame, text="Channel:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.channel_var = tk.StringVar(value="Unknown")
        ttk.Label(info_frame, textvariable=self.channel_var).grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        parent.rowconfigure(10, weight=1)
    
    def reset_ui(self):
        """Reset UI to initial state."""
        self.quality_combo['values'] = []
        self.quality_var.set("")
        self.quality_combo.state(['disabled'])
        self.download_btn.state(['disabled'])
        self.progress_var.set(0)
        self.progress_label.config(text="0%")
        self.status_var.set("Ready to download...")
        
        self.title_var.set("No video loaded")
        self.duration_var.set("--:--")
        self.channel_var.set("Unknown")
        
        self.video_info = None
        self.available_qualities = []
    
    def fetch_video_info(self):
        """Fetch video information in a separate thread."""
        url = self.url_var.get().strip()
        
        if not url:
            messagebox.showwarning("Warning", "Please enter a YouTube URL")
            return
        
        if not validate_youtube_url(url):
            messagebox.showerror("Error", "Invalid YouTube URL")
            return
        
        self.fetch_btn.state(['disabled'])
        self.status_var.set("Fetching video information...")
        
        def fetch_thread():
            try:
                self.video_info = self.downloader.get_video_info(url)
                
                if self.video_info:
                    self.available_qualities = self.downloader.get_available_qualities(self.video_info)
                    
                    self.root.after(0, self.update_video_info)
                else:
                    self.root.after(0, lambda: self.show_error("Failed to fetch video information"))
                    
            except Exception as e:
                self.root.after(0, lambda e=e: self.show_error(f"Error: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.fetch_btn.state(['!disabled']))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def update_video_info(self):
        """Update UI with fetched video information."""
        if not self.video_info:
            return
        
        self.title_var.set(self.video_info['title'])
        self.duration_var.set(format_duration(self.video_info['duration']))
        self.channel_var.set(self.video_info['uploader'])
        
        if self.available_qualities:
            self.quality_combo['values'] = self.available_qualities
            self.quality_var.set(self.available_qualities[0])
            self.quality_combo.state(['!disabled'])
            self.download_btn.state(['!disabled'])
            self.status_var.set("Ready to download")
        else:
            self.status_var.set("No downloadable formats found")
    
    def browse_output_directory(self):
        """Open directory browser for output selection."""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
    
    def start_download(self):
        """Start video download."""
        url = self.url_var.get().strip()
        quality = self.quality_var.get()
        output_path = self.output_var.get()
        
        if not url or not quality or not output_path:
            messagebox.showwarning("Warning", "Please fill all required fields")
            return
        
        self.download_btn.state(['disabled'])
        self.fetch_btn.state(['disabled'])
        self.status_var.set("Starting download...")
        
        self.downloader.download_video(
            url=url,
            quality=quality,
            output_path=output_path,
            progress_callback=self.update_progress,
            completion_callback=self.download_completed
        )
    
    def update_progress(self, progress_data):
        """Update progress bar and status."""
        percentage = progress_data.get('percentage', 0)
        speed = progress_data.get('speed', 0)
        eta = progress_data.get('eta', 0)
        
        self.root.after(0, lambda: self.progress_var.set(percentage))
        self.root.after(0, lambda: self.progress_label.config(text=f"{percentage:.1f}%"))
        
        if speed and eta:
            speed_str = format_bytes(speed) + "/s"
            status = f"Downloading... {speed_str} - ETA: {eta}s"
        else:
            status = "Downloading..."
        
        self.root.after(0, lambda: self.status_var.set(status))
    
    def download_completed(self, success, message):
        """Handle download completion."""
        self.root.after(0, lambda: self.download_btn.state(['!disabled']))
        self.root.after(0, lambda: self.fetch_btn.state(['!disabled']))
        
        if success:
            self.root.after(0, lambda: self.progress_var.set(100))
            self.root.after(0, lambda: self.progress_label.config(text="100%"))
            self.root.after(0, lambda: self.status_var.set("Download completed!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", message))
        else:
            self.root.after(0, lambda: self.status_var.set("Download failed"))
            self.root.after(0, lambda: messagebox.showerror("Error", message))
    
    def show_error(self, message):
        """Show error message."""
        self.status_var.set("Error occurred")
        messagebox.showerror("Error", message)