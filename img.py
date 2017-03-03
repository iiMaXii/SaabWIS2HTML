"""
Usage: script.py

This script extracts all images from the Saab WIS CD
"""

from glob import glob
import os
import zipfile

DIRECTORY = 'D:/9-5 (600)/package'
OUTPUT_DIRECTORY = 'static/data/images'

if not os.path.exists(OUTPUT_DIRECTORY):
    os.makedirs(OUTPUT_DIRECTORY)

for f in glob(os.path.join(DIRECTORY, "images[0-9]*.zip")):
    print('Extracting {0}'.format(f))
    with zipfile.ZipFile(f, 'r') as ziphandle:
        ziphandle.extractall(OUTPUT_DIRECTORY)
