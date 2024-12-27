from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
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