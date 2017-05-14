#!/usr/bin/env python3

import subprocess
import time
import concurrent.futures
import threading
import os
import sys
import win32api
import win32com.client
import pythoncom
import win32process
import pywintypes
import argparse

parser = argparse.ArgumentParser(description='Convert CAD drawings to images')
parser.add_argument('--output-path', type=str, required=True,
                    help='an integer for the accumulator')
parser.add_argument('input', type=str, nargs='+',
                    help='an integer for the accumulator')


args = parser.parse_args()

if not os.path.isdir(args.output_path):
    print('Error: Output directory does not exist')
    sys.exit(1)

pythoncom.CoInitialize()
client = win32com.client.dynamic.Dispatch('CADConverter.CADConverterX')

try:
    for input_file in args.input:
        file_name, _ = os.path.splitext(os.path.basename(input_file))
        output_file = os.path.join(args.output_path, file_name + '.png')

        client.convert(input_file, output_file, '-c PNG')
except pywintypes.com_error as e:
    sys.exit(2)

pythoncom.CoUninitialize()
