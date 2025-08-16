import yt_dlp
import os
import threading
from .utils import sanitize_filename, ensure_directory_exists, format_duration

class VideoDownloader:
    def __init__(self):
        self.download_thread = None
        self.is_downloading = False
        
    def get_video_info(self, url):
        """
        Get video information without downloading.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            dict: Video information or None if error
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown Channel'),
                    'thumbnail': info.get('thumbnail', ''),
                    'formats': info.get('formats', []),
                    'description': info.get('description', ''),
                    'view_count': info.get('view_count', 0),
                }
        except Exception as e:
            print(f"Error getting video info: {str(e)}")
            return None
    
    def get_available_qualities(self, url):
        """
        Get available video qualities for the URL.
        
        Args:
            url (str): YouTube video URL
            
        Returns:
            list: List of quality options
        """
        info = self.get_video_info(url)
        if not info:
            return []
        
        formats = info.get('formats', [])
        quality_map = {}
        
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                height = fmt.get('height')
                if height:
                    quality_key = f"{height}p"
                    ext = fmt.get('ext', 'mp4')
                    filesize = fmt.get('filesize', 0)
                    
                    if quality_key not in quality_map or (filesize and filesize > quality_map[quality_key].get('filesize', 0)):
                        quality_map[quality_key] = {
                            'format_id': fmt.get('format_id'),
                            'height': height,
                            'ext': ext,
                            'filesize': filesize,
                            'fps': fmt.get('fps', 0),
                        }
        
        audio_formats = [fmt for fmt in formats if fmt.get('vcodec') == 'none' and fmt.get('acodec') != 'none']
        if audio_formats:
            best_audio = max(audio_formats, key=lambda x: x.get('abr', 0))
            quality_map['Audio Only'] = {
                'format_id': best_audio.get('format_id'),
                'ext': best_audio.get('ext', 'mp3'),
                'filesize': best_audio.get('filesize', 0),
                'abr': best_audio.get('abr', 0),
            }
        
        sorted_qualities = []
        video_qualities = [k for k in quality_map.keys() if k != 'Audio Only']
        video_qualities.sort(key=lambda x: int(x.replace('p', '')), reverse=True)
        sorted_qualities.extend(video_qualities)
        
        if 'Audio Only' in quality_map:
            sorted_qualities.append('Audio Only')
        
        return sorted_qualities
    
    def download_video(self, url, quality, output_path, progress_callback=None, completion_callback=None):
        """
        Download video with selected quality.
        
        Args:
            url (str): YouTube video URL
            quality (str): Selected quality (e.g., '720p', 'Audio Only')
            output_path (str): Directory to save the video
            progress_callback (function): Callback for progress updates
            completion_callback (function): Callback for completion
        """
        def download_thread():
            try:
                self.is_downloading = True
                
                ensure_directory_exists(output_path)
                
                info = self.get_video_info(url)
                if not info:
                    if completion_callback:
                        completion_callback(False, "Failed to get video information")
                    return
                
                title = sanitize_filename(info['title'])
                
                if quality == 'Audio Only':
                    format_selector = 'bestaudio/best'
                    output_template = os.path.join(output_path, f"{title}.%(ext)s")
                else:
                    height = quality.replace('p', '')
                    format_selector = f"best[height<={height}]/best"
                    output_template = os.path.join(output_path, f"{title}.%(ext)s")
                
                def progress_hook(d):
                    if progress_callback and d['status'] == 'downloading':
                        try:
                            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                            downloaded_bytes = d.get('downloaded_bytes', 0)
                            
                            if total_bytes > 0:
                                percentage = (downloaded_bytes / total_bytes) * 100
                                speed = d.get('speed', 0)
                                eta = d.get('eta', 0)
                                
                                progress_callback({
                                    'percentage': percentage,
                                    'downloaded_bytes': downloaded_bytes,
                                    'total_bytes': total_bytes,
                                    'speed': speed,
                                    'eta': eta,
                                    'status': 'downloading'
                                })
                        except Exception as e:
                            print(f"Progress callback error: {e}")
                
                ydl_opts = {
                    'format': format_selector,
                    'outtmpl': output_template,
                    'progress_hooks': [progress_hook],
                    'quiet': True,
                    'no_warnings': True,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                    },
                }
                
                if quality == 'Audio Only':
                    ydl_opts['postprocessors'] = [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }]
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                if completion_callback:
                    completion_callback(True, f"Successfully downloaded: {title}")
                    
            except Exception as e:
                error_msg = f"Download failed: {str(e)}"
                print(error_msg)
                if completion_callback:
                    completion_callback(False, error_msg)
            finally:
                self.is_downloading = False
        
        if not self.is_downloading:
            self.download_thread = threading.Thread(target=download_thread)
            self.download_thread.daemon = True
            self.download_thread.start()
    
    def cancel_download(self):
        """Cancel ongoing download."""
        self.is_downloading = False