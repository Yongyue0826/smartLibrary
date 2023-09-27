import sys
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class MyMainWindow(QMainWindow):
    def __init__(self):
         super().__init__()
         self.initUI()

         def iniotUI(self):
             self.setWindowTitle("TARUMT Library")
             main_window = self.setGeometry(200, 200, 640, 480)
             
             central_widget = QWidget(main_window)
             self.setCentralWidget(central_widget)
             
             # Create a vertical layout to organize the buttons
             layout = QVBoxLayout(central_widget) 
             
             # Create three buttons
             video = QPushButton("open video window")
             button_B = QPushButton("function B")
             button_C = QPushButton("function C")
             
             # Add the buttons to the layout
             layout.addWidget(video)
             layout.addWidget(button_B)
             layout.addWidget(button_C)
             
             # Connect the buttons to their respective functions
             video.clicked.connect(open_video_window)
             button_B.clicked.connect(function_B)
             button_C.clicked.connect(function_C)

         def open_video_window():
            video_window = QDialog()
            video_window.setWindowTitle("Video Window")
            video_window.setGeometry(100, 100, 1500, 900)

            layout = QVBoxLayout(video_window)

            # Create a video player and video widget
            video_player = QMediaPlayer()
            video_widget = QVideoWidget()
            video_player.setVideoOutput(video_widget)

            layout.addWidget(video_widget)

            # Set the video file to play
            media = QMediaContent(QUrl.fromLocalFile('library.mp4'))
            video_player.setMedia(media)
            video_player.play()

            video_window.exec_()
        
        def function_B():
            a = 'try'
            return a 
        
        def function_C():
            b = 'try'
            return 
        
        
         
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MyMainWindow()
    mainWindow.show()
    sys.exit(app.exec_())