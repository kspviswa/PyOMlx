import pystray
from PIL import Image
import subprocess

process = None

def returnImage():
    return Image.open(r'logo.png')

def exit_app(icon, query):
    print('inside exit')
    global process
    process.terminate()
    process.wait()
    icon.stop()

def setup(icon: pystray.Icon):
    global process
    process = subprocess.Popen(['python3', 'serve.py'])
    icon.visible=True

def main() -> None:
    icon = pystray.Icon(name='test name',
                        visible=False,
                        icon=returnImage(),
                        title='PyOMlx',
                        menu=pystray.Menu(
                            pystray.MenuItem(
                                text="Close PyOMlx",
                                action=exit_app
                            ),
                        ))
    icon.title = 'pyOllama'
    icon.run(setup)
    

if __name__ == '__main__':
    main()
