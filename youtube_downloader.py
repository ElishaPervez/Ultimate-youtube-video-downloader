import sys
import os
import yt_dlp
from downloader_logic import DownloaderLogic

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QPushButton, QLabel, QLineEdit, QRadioButton,
                             QComboBox, QProgressBar, QTextEdit, QGroupBox, QSpacerItem,
                             QSizePolicy, QMessageBox, QFileDialog, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import QFont

# Worker for running yt-dlp in a separate thread
class Worker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(dict)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.function(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class YouTubeDownloader(QMainWindow):
    progress_update = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        self.video_info = None
        self.download_path = os.getcwd()
        self.logic = DownloaderLogic()

        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 700, 550)

        self.setup_theme()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        self.stacked_widget = QStackedWidget()
        self.opacity_effect = QGraphicsOpacityEffect(self.stacked_widget)
        self.stacked_widget.setGraphicsEffect(self.opacity_effect)
        self.main_layout.addWidget(self.stacked_widget)

        self.create_home_page()
        self.create_selection_page()
        self.create_config_page()
        self.create_download_page()
        
        self.connect_signals()

        self.show()

    def setup_theme(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #0c1a3e; color: #e0e0e0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel { font-size: 14px; }
            QLineEdit {
                background-color: #1a294f; border: 1px solid #3c4a6f;
                border-radius: 5px; padding: 8px; font-size: 14px;
            }
            QLineEdit:focus { border-color: #5a7ee5; }
            QPushButton {
                background-color: #5a7ee5; color: white; font-size: 14px;
                font-weight: bold; border: none; border-radius: 8px;
                padding: 10px 20px;
            }
            QPushButton:hover { background-color: #7a9eff; }
            QPushButton:pressed { background-color: #4a6dd5; }
            QPushButton:disabled { background-color: #4a5a8f; }
            QRadioButton { font-size: 14px; }
            QComboBox {
                background-color: #1a294f; border: 1px solid #3c4a6f;
                border-radius: 5px; padding: 8px;
            }
            QComboBox::drop-down { border: none; }
            QProgressBar {
                border: 1px solid #3c4a6f; border-radius: 5px;
                text-align: center; color: white;
            }
            QProgressBar::chunk { background-color: #5a7ee5; border-radius: 5px; }
            QTextEdit {
                background-color: #1a294f; border: 1px solid #3c4a6f;
                border-radius: 5px;
            }
            QGroupBox { font-weight: bold; font-size: 16px; }
        """)

    def connect_signals(self):
        self.fetch_button.clicked.connect(self.start_fetch_info)
        self.quick_download_button.clicked.connect(self.start_quick_download)
        self.sel_back_button.clicked.connect(lambda: self.switch_page(0))
        self.sel_next_button.clicked.connect(self.on_selection_next)
        self.cfg_back_button.clicked.connect(lambda: self.switch_page(1))
        self.cfg_download_button.clicked.connect(self.start_custom_download)
        self.home_button.clicked.connect(lambda: self.switch_page(0))
        self.video_radio.toggled.connect(self.populate_config_page)
        self.progress_update.connect(self.on_progress_update)

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        title = QLabel("YouTube Video Downloader")
        title.setFont(QFont('Segoe UI', 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("Paste YouTube URL here")
        self.url_entry.setMaximumWidth(600)
        button_layout = QHBoxLayout()
        self.fetch_button = QPushButton("Fetch Details")
        self.quick_download_button = QPushButton("Quick Download")
        button_layout.addWidget(self.fetch_button)
        button_layout.addWidget(self.quick_download_button)
        layout.addWidget(title)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.url_entry)
        layout.addSpacing(20)
        layout.addLayout(button_layout)
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.stacked_widget.addWidget(page)

    def create_selection_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        self.video_title_label = QLabel("Video Title Will Appear Here")
        self.video_title_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.video_title_label.setWordWrap(True)
        self.video_title_label.setAlignment(Qt.AlignCenter)
        self.channel_label = QLabel("Channel: ")
        self.channel_label.setAlignment(Qt.AlignCenter)
        group_box = QGroupBox("Select Download Type")
        group_box.setAlignment(Qt.AlignCenter)
        radio_layout = QHBoxLayout()
        self.video_radio = QRadioButton("Video")
        self.audio_radio = QRadioButton("Audio")
        self.video_radio.setChecked(True)
        radio_layout.addWidget(self.video_radio)
        radio_layout.addWidget(self.audio_radio)
        group_box.setLayout(radio_layout)
        button_layout = QHBoxLayout()
        self.sel_next_button = QPushButton("Next")
        self.sel_back_button = QPushButton("Back")
        button_layout.addWidget(self.sel_back_button)
        button_layout.addWidget(self.sel_next_button)
        layout.addWidget(self.video_title_label)
        layout.addWidget(self.channel_label)
        layout.addSpacing(30)
        layout.addWidget(group_box)
        layout.addSpacing(30)
        layout.addLayout(button_layout)
        self.stacked_widget.addWidget(page)

    def create_config_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        self.quality_group = QGroupBox("Select Quality (Video)")
        quality_layout = QVBoxLayout(self.quality_group)
        self.quality_combo = QComboBox()
        quality_layout.addWidget(self.quality_combo)
        format_group = QGroupBox("Select Format")
        format_layout = QVBoxLayout(format_group)
        self.format_combo = QComboBox()
        format_layout.addWidget(self.format_combo)
        button_layout = QHBoxLayout()
        self.cfg_download_button = QPushButton("Download")
        self.cfg_back_button = QPushButton("Back")
        button_layout.addWidget(self.cfg_back_button)
        button_layout.addWidget(self.cfg_download_button)
        layout.addWidget(self.quality_group)
        layout.addWidget(format_group)
        layout.addSpacing(30)
        layout.addLayout(button_layout)
        self.stacked_widget.addWidget(page)

    def create_download_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 50, 50, 50)
        self.status_label = QLabel("Downloading...")
        self.status_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.progress_bar = QProgressBar()
        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.home_button = QPushButton("Back to Home")
        self.home_button.setEnabled(False)
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_box)
        layout.addWidget(self.home_button, alignment=Qt.AlignCenter)
        self.stacked_widget.addWidget(page)

    def run_in_thread(self, function, *args, **kwargs):
        on_finish = kwargs.pop('on_finish')
        on_error = kwargs.pop('on_error')
        
        self.thread = QThread()
        self.worker = Worker(function, *args, **kwargs)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(on_finish)
        self.worker.error.connect(on_error)
        
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def set_ui_enabled(self, enabled):
        self.fetch_button.setEnabled(enabled)
        self.quick_download_button.setEnabled(enabled)

    def start_fetch_info(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "URL Error", "Please enter a valid YouTube URL.")
            return
        
        self.set_ui_enabled(False)
        self.fetch_button.setText("Fetching...")
        
        self.run_in_thread(
            self.logic.fetch_info,
            url,
            on_finish=self.on_fetch_success,
            on_error=self.on_fetch_error
        )

    def on_fetch_success(self, info):
        self.set_ui_enabled(True)
        self.fetch_button.setText("Fetch Details")
        self.video_info = info
        self.video_title_label.setText(info.get('title', 'N/A'))
        self.channel_label.setText(f"Channel: {info.get('uploader', 'N/A')}")
        self.switch_page(1)

    def on_fetch_error(self, error_msg):
        self.set_ui_enabled(True)
        self.fetch_button.setText("Fetch Details")
        QMessageBox.critical(self, "Fetch Error", f"Could not fetch video info:\n{error_msg}")

    def on_selection_next(self):
        self.populate_config_page()
        self.switch_page(2)

    def populate_config_page(self):
        self.quality_combo.clear()
        self.format_combo.clear()

        if self.video_radio.isChecked():
            self.quality_group.setVisible(True)

            allowed_resolutions = {'1080p', '720p', '480p', '360p', '240p', '144p'}
            added_resolutions = set()

            formats = [f for f in self.video_info.get('formats', []) if f.get('vcodec') != 'none' and f.get('acodec') == 'none' and f.get('height')]
            formats.sort(key=lambda f: f.get('height', 0), reverse=True)

            for f in formats:
                height = f.get('height')
                if not height:
                    continue

                resolution_label = f"{height}p"
                if resolution_label in allowed_resolutions and resolution_label not in added_resolutions:
                    # Prefer formats with higher fps for the same resolution
                    label = f"{height}p"
                    if f.get('fps'):
                        label += f" ({f['fps']}fps)"

                    self.quality_combo.addItem(label, f['format_id'])
                    added_resolutions.add(resolution_label)

            self.format_combo.addItems(["mp4", "mkv"])
        else:  # Audio
            self.quality_group.setVisible(False)
            self.format_combo.addItems(["mp3", "wav"])

    def start_quick_download(self):
        url = self.url_entry.text().strip()
        if not url:
            QMessageBox.warning(self, "URL Error", "Please enter a valid YouTube URL.")
            return
        
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
        }
        self.execute_download(url, ydl_opts)

    def start_custom_download(self):
        url = self.video_info.get('webpage_url')

        if self.video_radio.isChecked():
            quality_id = self.quality_combo.currentData()
            file_format = self.format_combo.currentText()
            ydl_opts = {
                # This is the crucial fix. It tells yt-dlp to get the selected video,
                # the best audio, and merge them. If that's not possible, fall back to
                # the best available pre-merged file.
                'format': f'{quality_id}+bestaudio/best',
                'outtmpl': os.path.join(self.download_path, f'%(title)s.{file_format}'),
            }
        else: # Audio
            file_format = self.format_combo.currentText()
            ydl_opts = {
                'format': 'bestaudio',
                'outtmpl': os.path.join(self.download_path, f'%(title)s.{file_format}'),
                'extract_audio': True,
                'audio_format': file_format,
            }
        self.execute_download(url, ydl_opts)

    def execute_download(self, url, ydl_opts):
        self.switch_page(3)
        self.log_box.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Preparing to download...")
        self.home_button.setEnabled(False)

        self.run_in_thread(
            self.logic.download,
            url,
            ydl_opts,
            on_finish=self.on_download_finished,
            on_error=self.on_download_error,
            progress_hook=self.progress_hook
        )

    def progress_hook(self, d):
        # This is called from the worker thread.
        # Emit a signal to safely update the GUI from the main thread.
        self.progress_update.emit(d)

    def on_progress_update(self, d):
        # This slot is connected to the signal and executes on the main thread.
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                percent = (d.get('downloaded_bytes', 0) / d['total_bytes']) * 100
                self.progress_bar.setValue(int(percent))
            self.log_box.append(f"Downloading: {d.get('_percent_str', '0.0%')} of {d.get('_total_bytes_str', 'N/A')} at {d.get('_speed_str', 'N/A')}")
        elif d['status'] == 'finished':
            self.log_box.append(f"Finished downloading, now converting...")
            self.progress_bar.setValue(100)

    def on_download_finished(self, result):
        self.status_label.setText("Download Complete!")
        self.log_box.append("\nSuccessfully downloaded!")
        self.home_button.setEnabled(True)

    def on_download_error(self, error_msg):
        self.status_label.setText("Download Failed!")
        self.log_box.append(f"\nERROR: {error_msg}")
        self.home_button.setEnabled(True)

    def switch_page(self, index):
        if self.stacked_widget.currentIndex() == index:
            return

        self.anim_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_out.setDuration(200)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.InQuad)
        self.anim_out.finished.connect(lambda: self.change_widget_and_fade_in(index))
        self.anim_out.start()

    def change_widget_and_fade_in(self, index):
        self.stacked_widget.setCurrentIndex(index)

        self.anim_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim_in.setDuration(200)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.OutQuad)
        self.anim_in.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = YouTubeDownloader()
    main_win.show()
    sys.exit(app.exec_())
