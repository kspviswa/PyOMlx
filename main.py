from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
import subprocess
import os

basedir = os.path.dirname(__file__)
script_path = (os.path.join(basedir, "scripts", "serve.py"))
process = subprocess.Popen(['python3', script_path])

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

def stopServer():
    global process
    process.terminate()
    process.wait()
    app.quit()

# Create the icon
icon = QIcon(os.path.join(basedir, "icons", "logo.png"))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Add a Quit option to the menu.
menu = QMenu()
quit = QAction("Quit")
quit.triggered.connect(stopServer)
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

app.exec()