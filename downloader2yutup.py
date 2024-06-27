import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMainWindow, QAction, QMessageBox, QFileDialog, QComboBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
from pytube import YouTube
from pydub import AudioSegment

class Downloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Downloader")
        self.setGeometry(100, 100, 400, 250)

        self.menu_bar = self.menuBar()

        # Menu File
        file_menu = self.menu_bar.addMenu("File")

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu About
        about_menu = self.menu_bar.addMenu("About")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_message)
        about_menu.addAction(about_action)

        layout = QVBoxLayout()

        self.label_url = QLabel("Enter YouTube Video URL:")
        layout.addWidget(self.label_url)

        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.label_quality = QLabel("Select Video Quality:")
        layout.addWidget(self.label_quality)

        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Highest Resolution")
        self.quality_combo.addItem("Lowest Resolution")
        layout.addWidget(self.quality_combo)

        self.download_video_button = QPushButton("Download Video")
        self.download_video_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_video_button)

        self.download_audio_button = QPushButton("Download MP3")
        self.download_audio_button.clicked.connect(self.download_audio)
        layout.addWidget(self.download_audio_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def download_video(self):
        url = self.url_input.text()
        if url:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Video", "", "MP4 Files (*.mp4)")
            if file_path:
                self.download_youtube(url, file_path)
        else:
            self.status_label.setText("Enter a valid URL.")

    def download_audio(self):
        url = self.url_input.text()
        if url:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio", "", "MP3 Files (*.mp3)")
            if file_path:
                self.download_audio_thread = DownloadAudioThread(url, file_path, self.quality_combo.currentText())
                self.download_audio_thread.progress.connect(self.update_progress)
                self.download_audio_thread.start()
        else:
            self.status_label.setText("Enter a valid URL.")

    def download_youtube(self, url, file_path):
        try:
            yt = YouTube(url)
            if self.quality_combo.currentText() == "Highest Resolution":
                video = yt.streams.get_highest_resolution()
            elif self.quality_combo.currentText() == "Lowest Resolution":
                video = yt.streams.get_lowest_resolution()
            else:
                video = yt.streams.get_highest_resolution()

            video.download(output_path=file_path.rsplit("/", 1)[0], filename=file_path.rsplit("/", 1)[1])
            self.status_label.setText("Video downloaded successfully.")
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")

    def show_about_message(self):
        QMessageBox.about(self, "About", "Copyright Ibnulsahgianto 2024")

    def update_progress(self, progress):
        self.progress_bar.setValue(progress)

class DownloadAudioThread(QThread):
    progress = pyqtSignal(int)

    def __init__(self, url, file_path, quality):
        super().__init__()
        self.url = url
        self.file_path = file_path
        self.quality = quality

    def run(self):
        try:
            yt = YouTube(self.url)
            stream = yt.streams.filter(only_audio=True).first()
            video_file_path = self.file_path.rsplit("/", 1)[0] + "/" + self.file_path.rsplit("/", 1)[1].replace(".mp3", ".mp4")
            stream.download(output_path=self.file_path.rsplit("/", 1)[0], filename=self.file_path.rsplit("/", 1)[1].replace(".mp3", ".mp4"))
            
            # Convert the downloaded audio file to MP3
            audio = AudioSegment.from_file(video_file_path, format="mp4")
            audio.export(self.file_path, format="mp3")

            # Delete the temporary video file
            os.remove(video_file_path)

            self.progress.emit(100)  # Signal completion
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Downloader()
    window.show()
    sys.exit(app.exec_())
