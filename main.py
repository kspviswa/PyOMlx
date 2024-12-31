from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
import subprocess
import os
import sys

basedir = os.path.dirname(__file__)
script_base_path = os.path.join(basedir, "scripts")
script_path = (os.path.join(basedir, "scripts", "launch.sh"))
result = subprocess.run(['/bin/bash', script_path, script_base_path])

app = QApplication([])
app.setQuitOnLastWindowClosed(False)

if result.returncode == 1:
    QMessageBox.critical(
        None,  # Parent widget (None means it will be a top-level window)
        "Error",  # Title of the message box
        "PyOMlx cannot be started due to some error. Check logs in /tmp/pyomlx-*.log",  # Message text
        QMessageBox.Ok  # Buttons to display
    )
    sys.exit(1)

def stopServer():
    stop_script_path = (os.path.join(basedir, "scripts", "stop.sh"))
    subprocess.run(['/bin/sh', stop_script_path])
    app.quit()

def showAbout():
    ab = QMessageBox()
    ab.setText("PyOMlx \n\n Version 0.1.0 \n Copyright Viswa Kumar ©️ 2024")
    ab.exec()

# Create the icon
icon = QIcon(os.path.join(basedir, "logo.png"))

# Create the tray
tray = QSystemTrayIcon()
tray.setIcon(icon)
tray.setVisible(True)

# Add a Quit option to the menu.
menu = QMenu()
quit = QAction("Quit")
about = QAction('About')
quit.triggered.connect(stopServer)
about.triggered.connect(showAbout)
menu.addAction(about)
menu.addAction(quit)

# Add the menu to the tray
tray.setContextMenu(menu)

app.exec()