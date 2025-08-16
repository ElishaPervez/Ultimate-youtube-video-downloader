# YouTube Video Downloader

A simple, user-friendly GUI application for downloading YouTube videos with quality selection.

## Features

- **Simple Interface**: Clean, intuitive GUI built with tkinter/PyQt5
- **Quality Selection**: Choose from available video qualities (720p, 1080p, 480p, audio-only)
- **Real-time Progress**: Live download progress tracking
- **Video Information**: Display video title, duration, and channel details
- **Flexible Output**: Choose custom download location

## Requirements

- Python 3.7+
- yt-dlp
- tkinter (built-in with Python) or PyQt5

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/youtube-video-downloader.git
   cd youtube-video-downloader
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

## Usage

1. **Enter URL**: Paste a YouTube video URL into the input field
2. **Fetch Info**: Click "Fetch Info" to load video details and available qualities
3. **Select Quality**: Choose your preferred video quality from the dropdown
4. **Choose Location**: Select where to save the downloaded video
5. **Download**: Click "Download Video" to start the download

## Project Structure

```
youtube-video-downloader/
├── main.py              # Application entry point
├── gui.py               # GUI components and layout
├── downloader.py        # yt-dlp integration and download logic
├── utils.py             # Helper functions and utilities
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Supported URLs

- Standard YouTube URLs: `https://www.youtube.com/watch?v=VIDEO_ID`
- Short URLs: `https://youtu.be/VIDEO_ID`
- Playlist URLs: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

## Future Features

- [ ] Batch downloads from playlists
- [ ] Audio-only downloads with format selection
- [ ] Download history and queue management
- [ ] Custom filename templates
- [ ] Subtitle download options
- [ ] Dark/light theme toggle
- [ ] Configuration settings
- [ ] Resume interrupted downloads

## Dependencies

- **yt-dlp**: YouTube video downloading engine
- **tkinter/PyQt5**: GUI framework
- **threading**: For non-blocking downloads

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This tool is for educational and personal use only. Please respect YouTube's Terms of Service and content creators' rights. Only download content you have permission to download.

## Troubleshooting

**Common Issues:**

- **"yt-dlp not found"**: Ensure yt-dlp is installed (`pip install yt-dlp`)
- **Permission errors**: Run with appropriate permissions or choose a different output directory
- **Network errors**: Check your internet connection and try again

**Getting Help:**

- Check the [Issues](https://github.com/yourusername/youtube-video-downloader/issues) page
- Create a new issue with detailed error information
- Include your Python version and operating system