#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import re
import os
import zipfile
import sys

DIRECTORY = 'D:\\'
MODEL = '9-5 (600)'

OUTPUT_DIRECTORY = 'static/data'

# Step 1
"""
def get_language_codes():
    language_codes = []

    for f in glob.glob(os.path.join(DIRECTORY, MODEL, "package/*.zip")):
        f = os.path.basename(f)
        match = re.match('([a-z]{2})[0-9]{1,2}.zip$', f)

        if match:

            lc = match.group(1)
            print(lc)
            if lc not in language_codes:
                language_codes.append(lc)

    return sorted(language_codes)

print('Available languages:', get_language_codes())

language_code = 'se'

destination_directory = os.path.join(OUTPUT_DIRECTORY, language_code.lower())

if not os.path.exists(destination_directory):
    os.makedirs(destination_directory)

print(os.path.join(DIRECTORY, MODEL, "package", language_code.lower()+"*.zip"))

for f in glob.glob(os.path.join(DIRECTORY, MODEL, "package", language_code.lower()+"*.zip")):
    print('Extracting {0}'.format(f))
    with zipfile.ZipFile(f, 'r') as ziphandle:
        ziphandle.extractall(destination_directory)

"""
# Step 2

from bs4 import BeautifulSoup
import os
import codecs
import collections
import json

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

soup = BeautifulSoup(open('C:/Users/iiMaXii/PycharmProjects/SaabWIS2HTML/static/data/views/9-5 (9600)2006se.xml', 'r'), 'html.parser')

# print(soup.prettify())

print("carmodel    : ", soup.modelyear['carmodel'])
print("modelnumber : ", soup.modelyear['modelnumber'])
print("modelnumber : ", soup.modelyear['modelyear'])
print("language    : ", soup.modelyear['language'])

language_code = soup.modelyear['language']

OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, language_code.lower(), 'index')

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

tree_data = []

tab_dict = {}
tabs = []

# output_2 = codecs.open(os.path.join(OUTPUT_DIRECTORY, sc_id + '.html'), 'w', 'utf-8')
submenus = {}

for sct in soup.findAll('sct'):
    tree_data.append({
        'text': sct.find('name').contents[0],
        'nodes': [],
    })

    for sc in sct.findAll('sc'):
        sc_id = sc['id']
        tree_data[-1]['nodes'].append({
            'text': sc.find('name').contents[0],
            'href': '#{}'.format(sc_id),
            'data-id': sc_id,
        })
        print('\t',sc.find('name').contents[0], '({})'.format(sc_id))

        submenus[sc_id] = {}
        for sit in sc.findAll('sit'):
            tab_dict[sit['num']] = sit.find('name').contents[0]

            submenus[sc_id][sit['num']] = []

            for sie in sit.findAll('sie'):

                children = []

                sie_elements = sie.findAll('sisub')
                if sie_elements:
                    for sisub in sie.findAll('sisub'):
                        sisub_name_contents = sisub.find('name').contents  # name tag might be empty for unkown reason
                        sisub_name = sisub_name_contents[0] if sisub_name_contents else 'null'

                        children.append({
                            'data-id': sisub['sisubid'],
                            'text': sisub_name,
                        })

                submenu = {
                    'data-id': sie['docid'],
                    'text': sie.find('name').contents[0],
                }
                if children:
                    submenu['nodes'] = children

                submenus[sc_id][sit['num']].append(submenu)

with open(os.path.join(OUTPUT_DIRECTORY, 'menu.json'), 'w') as outfile:
    json.dump(tree_data, outfile)

for key, value in sorted(tab_dict.items()):
    tabs.append({
        'id': key,
        'name': value,
    })

with open(os.path.join(OUTPUT_DIRECTORY, 'tabs.json'), 'w') as outfile:
    json.dump(tabs, outfile)

with open(os.path.join(OUTPUT_DIRECTORY, 'submenus.json'), 'w') as outfile:
    json.dump(submenus, outfile)
