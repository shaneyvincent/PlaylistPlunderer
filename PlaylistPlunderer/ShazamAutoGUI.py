import sys
import subprocess
import threading
from shazam_automation import run_automation
import os
import signal
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QCoreApplication
import platform  # New import for checking the operating system
from webdriver_manager.chrome import ChromeDriverManager  # New import for managing ChromeDriver
import shazam_automation


class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

    def flush(self):
        pass

class CustomFramelessWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.shazam_process = None
        self.num_iterations = "3"  # Default to 3 iterations
        self.isResizing = False
        self.isDragging = False
        self.dragPosition = QtCore.QPoint()
        self.appDirectory = os.path.dirname(os.path.abspath(__file__))
        self.originalPixmap = QtGui.QPixmap(os.path.join(self.appDirectory, "resources", "beeper.png"))
        self.alternatePixmap = QtGui.QPixmap(os.path.join(self.appDirectory, "resources", "beeperonstate.png"))

        self.aspectRatio = self.originalPixmap.width() / self.originalPixmap.height()
        self.scaledAlternatePixmap = self.alternatePixmap.scaled(self.originalPixmap.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.initUI()

    def initUI(self):
        initialWidth = 600
        initialHeight = int(initialWidth / self.aspectRatio)
        self.setGeometry(300, 300, initialWidth, initialHeight)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.backgroundLabel = QtWidgets.QLabel(self)
        self.backgroundLabel.setPixmap(self.originalPixmap.scaled(initialWidth, initialHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.backgroundLabel.setScaledContents(True)

        self.loadCustomFont()

        self.buttonPositions = [
            {"name": "Button 1", "x": 120, "y": 318, "width": 164, "height": 90},
            {"name": "Button 2", "x": 292, "y": 317, "width": 159, "height": 110},
            {"name": "Button 3", "x": 460, "y": 320, "width": 220, "height": 120},
            {"name": "Button 4", "x": 696, "y": 340, "width": 221, "height": 150}
        ]
        self.screenAreaInfo = {"name": "Screen Area", "x": 130, "y": 131, "width": 674, "height": 138}
        self.createScreenArea()
        self.createButtons()

        # Initialize the output text box with specific geometry and style
        self.initOutputTextBox()

        self.resizeHandle = QtWidgets.QLabel(self)
        self.resizeHandle.setGeometry(initialWidth - 20, initialHeight - 20, 20, 20)
        self.resizeHandle.setStyleSheet("background-color: #3b1a4a;")
        self.resizeHandle.setCursor(QtCore.Qt.SizeFDiagCursor)
        self.resizeHandle.mousePressEvent = self.resizeHandleMousePressEvent
        self.resizeHandle.mouseMoveEvent = self.resizeHandleMouseMoveEvent
        self.resizeHandle.mouseReleaseEvent = self.resizeHandleMouseReleaseEvent

        self.setMinimumSize(300, int(300 / self.aspectRatio))
        max_width = int(self.originalPixmap.width() * 1.15)
        max_height = int(self.originalPixmap.height() * 1.15)
        self.setMaximumSize(max_width, max_height)

        self.btnClose = QtWidgets.QPushButton("", self)
        closeButtonStyle = """
            QPushButton {
                background-color: #ed6a5f;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #d45146;
            }
        """
        self.btnClose.setStyleSheet(closeButtonStyle)
        self.btnClose.setGeometry(10, 2, 12, 12)
        self.btnClose.clicked.connect(self.close)

        self.btnMinimize = QtWidgets.QPushButton("", self)
        minimizeButtonStyle = """
            QPushButton {
                background-color: #f4be4f;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #dfa939;
            }
        """
        self.btnMinimize.setStyleSheet(minimizeButtonStyle)
        self.btnMinimize.setGeometry(30, 2, 12, 12)
        self.btnMinimize.clicked.connect(self.showMinimized)

        # Dropdown menu for number of iterations
        self.iteration_menu = QtWidgets.QComboBox(self)
        self.iteration_menu.addItems(["1", "2", "3"])
        self.iteration_menu.setCurrentIndex(2)  # Default to 3 iterations
        self.iteration_menu.move(180, 97)  # Initial position for the drop-down menu
        self.iteration_menu.resize(170, 31)  # Initial size for the drop-down menu
        initialFontSize = 10  # Adjust this as needed
        font = self.iteration_menu.font()
        font.setPointSize(initialFontSize)
        self.iteration_menu.setFont(font)
        self.iteration_menu.currentIndexChanged.connect(self.iteration_selection_changed)
        self.iteration_menu.setStyleSheet("""
            QComboBox {
                background-color: #1f0d29;  /* Background color */
                color: #e0bb0c;            /* Text color */
                border: 1px solid #1f0d29; /* Border color */
                border-radius: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url('path_to_down_arrow_icon.png'); /* Path to the drop-down arrow image */
            }
            QComboBox QAbstractItemView {
                background-color: #3b1a4a;  /* Background color of the drop-down list */
                color: #e0bb0c;            /* Text color in the drop-down list */
                selection-background-color: #606060; /* Background color of the selected item */
            }
        """)
    def loadCustomFont(self):
        # Change the path to the new font file
        font_path = os.path.join(self.appDirectory, "resources", "tiny-islanders-font", "TinyIslanders-nOYg.ttf")

        font_id = QtGui.QFontDatabase.addApplicationFont(font_path)
        
        if font_id != -1:
            # Getting the family name of the font
            font_family = QtGui.QFontDatabase.applicationFontFamilies(font_id)[0]
            self.customFont = QtGui.QFont(font_family, 10)  # You can adjust the size
        else:
            print("Failed to load custom font.")
            self.customFont = QtGui.QFont("Arial", 10)  # Fallback font

    def initOutputTextBox(self):
        self.outputTextBox = QtWidgets.QTextEdit(self)
        self.updateOutputTextBoxGeometry()  # Set initial geometry
        self.outputTextBox.setStyleSheet("QTextEdit { background-color: white; color: black; }")
        self.outputTextBox.setReadOnly(True)
        self.outputTextBox.ensureCursorVisible()
        self.outputTextBox.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.outputTextBox.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        # Set the custom font for the text box
        self.outputTextBox.setFont(self.customFont)

        # Redirect standard output to the text box
        sys.stdout = Stream(newText=self.onUpdateText)

    def updateOutputTextBoxGeometry(self):
        # Calculate the geometry based on the window size
        scaleFactorX = self.width() / self.originalPixmap.width()
        scaleFactorY = self.height() / self.originalPixmap.height()
        newX = int(155 * scaleFactorX)
        newY = int(155 * scaleFactorY)
        newWidth = int(629 * scaleFactorX)
        newHeight = int(100 * scaleFactorY)
        self.outputTextBox.setGeometry(newX, newY, newWidth, newHeight)
        fontSize = max(8, int(27 * scaleFactorX))  # Adjust font size based on scale
        self.outputTextBox.setStyleSheet(f"QTextEdit {{ background-color: transparent; color: #3b4e53; font-size: {fontSize}px; }}")


    def onUpdateText(self, text):
        self.outputTextBox.moveCursor(QtGui.QTextCursor.End)
        self.outputTextBox.insertPlainText(text)
        self.outputTextBox.ensureCursorVisible()

    # [Continues in the next message...]
    # ... Previous methods ...

    def createScreenArea(self):
        self.screenAreaLabel = QtWidgets.QLabel(self)
        self.updateScreenAreaLabelGeometry()
        self.screenAreaLabel.hide()

    def updateScreenAreaLabelGeometry(self):
        scaleFactorX = self.width() / self.originalPixmap.width()
        scaleFactorY = self.height() / self.originalPixmap.height()
        newX = int(self.screenAreaInfo["x"] * scaleFactorX)
        newY = int(self.screenAreaInfo["y"] * scaleFactorY)
        newWidth = int(self.screenAreaInfo["width"] * scaleFactorX)
        newHeight = int(self.screenAreaInfo["height"] * scaleFactorY)
        self.screenAreaLabel.setGeometry(newX, newY, newWidth, newHeight)

    def createButtons(self):
        self.buttons = []
        self.buttonLabels = []
        for buttonInfo in self.buttonPositions:
            button = QtWidgets.QPushButton("", self)
            button.setGeometry(buttonInfo["x"], buttonInfo["y"], buttonInfo["width"], buttonInfo["height"])
            button.setStyleSheet("background-color: transparent; border: none;")
            button.pressed.connect(lambda bi=buttonInfo: self.handleButtonPress(bi))
            button.released.connect(lambda bi=buttonInfo: self.handleButtonRelease(bi))
            self.buttons.append(button)

            label = QtWidgets.QLabel(self)
            label.setGeometry(buttonInfo["x"], buttonInfo["y"], buttonInfo["width"], buttonInfo["height"])
            label.hide()
            self.buttonLabels.append(label)

    def handleButtonPress(self, buttonInfo):
        self.showAlternateImage(buttonInfo)
        if buttonInfo['name'] == "Button 3":
            self.stop_shazam()
        elif buttonInfo['name'] == "Button 4":
            self.start_shazam()

    def handleButtonRelease(self, buttonInfo):
        self.hideAlternateImages()

    def showAlternateImage(self, buttonInfo):
        scaleFactorX = self.width() / self.originalPixmap.width()
        scaleFactorY = self.height() / self.originalPixmap.height()
        for label, info in zip(self.buttonLabels, self.buttonPositions):
            if info == buttonInfo:
                newX = int(info["x"] * scaleFactorX)
                newY = int(info["y"] * scaleFactorY)
                newWidth = int(info["width"] * scaleFactorX)
                newHeight = int(info["height"] * scaleFactorY)
                pixmap = self.scaledAlternatePixmap.copy(newX, newY, newWidth, newHeight)
                label.setPixmap(pixmap)
                label.show()

    def hideAlternateImages(self):
        for label in self.buttonLabels:
            label.hide()

    def updateScreenArea(self, alternate):
        if alternate:
            self.showSpecificAreaAlternateImage(self.screenAreaLabel, self.screenAreaInfo)
        else:
            self.screenAreaLabel.hide()

    def showSpecificAreaAlternateImage(self, label, areaInfo):
        scaleFactorX = self.width() / self.originalPixmap.width()
        scaleFactorY = self.height() / self.originalPixmap.height()
        newX = int(areaInfo["x"] * scaleFactorX)
        newY = int(areaInfo["y"] * scaleFactorY)
        newWidth = int(areaInfo["width"] * scaleFactorX)
        newHeight = int(areaInfo["height"] * scaleFactorY)
        pixmap = self.scaledAlternatePixmap.copy(newX, newY, newWidth, newHeight)
        label.setPixmap(pixmap)
        label.show()

    # [Continues in the next message...]
    # ... Previous methods ...

    def iteration_selection_changed(self, index):
        self.num_iterations = self.iteration_menu.itemText(index)

    def run_shazam_automation(self):
        command = [sys.executable, os.path.join(self.appDirectory, "shazam_automation.py"), self.num_iterations]
        self.shazam_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=self.read_process_output, daemon=True).start()


        
    def read_process_output(self):
        if self.shazam_process:
            while True:
                output = self.shazam_process.stdout.readline()
                if output == '' and self.shazam_process.poll() is not None:
                    break
                if output:
                    self.update_text_box(output.strip())
        else:
            print("Shazam process is not running.")


    def update_text_box(self, text):
        # Safely update the text box in the main thread
        QtCore.QMetaObject.invokeMethod(self.outputTextBox, "insertPlainText", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(str, text + '\n'))


    def start_shazam(self):
        # Ensure num_iterations is an integer
        num_iterations = int(self.num_iterations)
    
        # Start run_automation in a thread to prevent UI freezing
        thread = threading.Thread(target=self.run_automation_wrapper, args=(num_iterations,))
        thread.daemon = True  # Ensures thread closes with the application
        thread.start()

    def run_automation_wrapper(self, num_iterations):
        # Call the modified run_automation function that returns results
        shazam_results = run_automation(num_iterations)
    
        # Process the results (update the GUI based on results)
        # Ensure GUI updates are done in the main thread
        self.handle_shazam_results(shazam_results)

    def handle_shazam_results(self, shazam_results):
        # This function is intended to process the results
        # Example: updating a text field with the results
        # Make sure to update the GUI in a thread-safe way
        QCoreApplication.postEvent(self, CustomEvent(shazam_results))

    def stop_shazam(self):
        # Signal the shazam_automation script to stop
        if self.shazam_process and self.shazam_process.is_alive():
            shazam_automation.should_stop = True
            self.shazam_process.join()  # Wait for the thread to finish
        
        self.shazam_process = None
        self.updateScreenArea(False)
        self.outputTextBox.insertPlainText("Shazam automation stopped.\n")



    def resizeHandleMousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.isResizing = True
            self.resizeStartPosition = event.globalPos()

    def resizeHandleMouseMoveEvent(self, event):
        if self.isResizing:
            delta = event.globalPos() - self.resizeStartPosition
            newWidth = self.width() + delta.x()
            newHeight = self.height() + delta.y()
            newHeight = max(newHeight, int(newWidth / self.aspectRatio))
            self.resize(newWidth, newHeight)
            self.resizeStartPosition = event.globalPos()

    def resizeHandleMouseReleaseEvent(self, event):
        self.isResizing = False

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and not self.isResizing:
            self.isDragging = True
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.isDragging and event.buttons() == QtCore.Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)

    def mouseReleaseEvent(self, event):
        self.isDragging = False

    def resizeEvent(self, event):
        newWidth = event.size().width()
        newHeight = int(newWidth / self.aspectRatio)
        self.resize(newWidth, newHeight)
        self.backgroundLabel.setPixmap(self.originalPixmap.scaled(newWidth, newHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        self.scaledAlternatePixmap = self.alternatePixmap.scaled(newWidth, newHeight, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.backgroundLabel.setGeometry(0, 0, newWidth, newHeight)
        self.updateButtonPositions(newWidth, newHeight)
        self.updateScreenAreaLabelGeometry()
        self.updateOutputTextBoxGeometry()
        if self.shazam_process is not None:
            self.updateScreenArea(True)  # Update the alternate image for screen area
        self.resizeHandle.move(newWidth - 20, newHeight - 20)
        self.btnClose.move(10, 2)
        self.btnMinimize.move(30, 2)
        self.updateDropdownMenu(newWidth, newHeight)
        super().resizeEvent(event)


    def updateButtonPositions(self, width, height):
        scaleFactorX = width / self.originalPixmap.width()
        scaleFactorY = height / self.originalPixmap.height()
        for button, label, position in zip(self.buttons, self.buttonLabels, self.buttonPositions):
            newX = int(position["x"] * scaleFactorX)
            newY = int(position["y"] * scaleFactorY)
            newWidth = int(position["width"] * scaleFactorX)
            newHeight = int(position["height"] * scaleFactorY)
            button.setGeometry(newX, newY, newWidth, newHeight)
            label.setGeometry(newX, newY, newWidth, newHeight)

    def updateDropdownMenu(self, width, height):
        scaleFactorX = width / self.originalPixmap.width()
        scaleFactorY = height / self.originalPixmap.height()
        newMenuX = int(180 * scaleFactorX)
        newMenuY = int(97 * scaleFactorY)
        newMenuWidth = int(170 * scaleFactorX)
        newMenuHeight = int(31 * scaleFactorY)
        self.iteration_menu.move(newMenuX, newMenuY)
        self.iteration_menu.resize(newMenuWidth, newMenuHeight)

        self.iteration_menu.setStyleSheet("""
            QComboBox {
                background-color: #1f0d29;  /* Background color */
                color: #e0bb0c;            /* Text color */
                border: 1px solid #1f0d29; /* Border color */
                border-radius: 4px;
                margin: 0px;  /* Remove margin */
                padding: 0px; /* Remove padding */
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url('path_to_down_arrow_icon.png'); /* Path to the drop-down arrow image */
            }
            QComboBox QAbstractItemView {
                background-color: #3b1a4a;  /* Background color of the drop-down list */
                color: #e0bb0c;            /* Text color in the drop-down list */
                selection-background-color: #606060; /* Background color of the selected item */
                margin: 0px;  /* Remove margin */
                padding: 0px; /* Remove padding */
            }
        """)

def main():
    app = QtWidgets.QApplication(sys.argv)
    iconPath = "/Users/Shaney/Documents/PlaylistPlunderer/appicondesk.icns"
    app.setWindowIcon(QtGui.QIcon(iconPath))
    ex = CustomFramelessWindow()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
