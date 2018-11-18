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

"""for f in glob(os.path.join(DIRECTORY, "images[0-9]*.zip")):
    print('Extracting {0}'.format(f))
    with zipfile.ZipFile(f, 'r') as ziphandle:
        ziphandle.extractall(OUTPUT_DIRECTORY)"""

FAULT_FINDER_DIRECTORY = os.path.join(DIRECTORY, 'faultfinder', 'images')
FAULT_FINDER_OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, 'faultfinder')

if not os.path.exists(FAULT_FINDER_OUTPUT_DIRECTORY):
    os.makedirs(FAULT_FINDER_OUTPUT_DIRECTORY)

for f in glob(os.path.join(DIRECTORY, "images[0-9]*.zip")):
    print('Extracting {0}'.format(f))
    with zipfile.ZipFile(f, 'r') as ziphandle:
        ziphandle.extractall(FAULT_FINDER_OUTPUT_DIRECTORY)
