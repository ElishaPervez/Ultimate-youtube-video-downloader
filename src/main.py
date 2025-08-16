#!/usr/bin/env python3
"""
YouTube Video Downloader
A simple GUI application for downloading YouTube videos using yt-dlp.
"""

import tkinter as tk
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import yt_dlp
    except ImportError:
        print("Error: yt-dlp is not installed.")
        print("Please install it using: pip install yt-dlp")
        return False
    return True

def main():
    """Main application entry point."""
    if not check_dependencies():
        sys.exit(1)
    
    try:
        from .gui import YouTubeDownloaderGUI
        
        root = tk.Tk()
        
        try:
            root.iconbitmap('icon.ico')
        except:
            pass
        
        app = YouTubeDownloaderGUI(root)
        
        def on_closing():
            """Handle application closing."""
            if app.downloader.is_downloading:
                from tkinter import messagebox
                if messagebox.askokcancel("Quit", "Download is in progress. Do you want to quit?"):
                    app.downloader.cancel_download()
                    root.destroy()
            else:
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("YouTube Video Downloader started successfully!")
        print("GUI is now running...")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()