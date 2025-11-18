import sys
from datetime import datetime

from PyQt5.QtGui import QGuiApplication


def paste_image_main():
    app = QGuiApplication(sys.argv)
    clipboard = app.clipboard()
    
    if not clipboard:
        print("No clipboard")
        sys.exit(1)

    if not clipboard.mimeData().hasImage():
        print("No image in clipboard")
        sys.exit(1)

    image = clipboard.image()
    filename = datetime.now().isoformat().replace(":",".") + ".png"   # shitty messysoft os cannot stand colons in filenames
    image.save(filename)
    print(filename)
