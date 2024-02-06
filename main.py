from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
import subprocess
import os

basedir = os.path.dirname(__file__)
script_base_path = os.path.join(basedir, "scripts")
script_path = (os.path.join(basedir, "scripts", "launch.sh"))
subprocess.run(['/bin/sh', script_path, script_base_path])

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

def stopServer():
    stop_script_path = (os.path.join(basedir, "scripts", "stop.sh"))
    subprocess.run(['/bin/sh', stop_script_path])
    app.quit()

# Create the icon
icon = QIcon(os.path.join(basedir, "logo.png"))

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