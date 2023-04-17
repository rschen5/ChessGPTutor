# script for resizing images
# citation:
# https://stackoverflow.com/questions/21517879/python-pil-resize-all-images-in-a-folder
#!/usr/bin/python
from PIL import Image
import os, sys
IMAGE_PATH = "./images/"

dirs = os.listdir( IMAGE_PATH )

def resize():
    for item in dirs:
        if os.path.isfile(IMAGE_PATH+item):
            if '.DS_Store' not in item:
                im = Image.open(IMAGE_PATH+item)
                f, e = os.path.splitext(IMAGE_PATH+item)
                imResize = im.resize((100,100))
                imResize.save(f+".png", 'PNG')

resize()
