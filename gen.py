""" Generate link lookup tables depending on car model and year.
"""

"""
Directory structure: 
 - static/
   - data/
     - 

9-5 (9600)/2006/
 - menu.json (tree for first menu)
 - tabs.json (tabs)
 - submenus.json
 - references.json (linkid -> docid)

/c(\d+)
<sc num="(\d+)">
"""

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
import json

soup = BeautifulSoup(open('C:/Users/iiMaXii/PycharmProjects/SaabWIS2HTML/static/data/views/9-5 (9600)2006se.xml', 'r'), 'html.parser')

print("carmodel    :", soup.modelyear['carmodel'])
print("modelnumber :", soup.modelyear['modelnumber'])
print("modelyear   :", soup.modelyear['modelyear'])
print("language    :", soup.modelyear['language'])

language_code = soup.modelyear['language']

OUTPUT_DIRECTORY = os.path.join(OUTPUT_DIRECTORY, language_code.lower(), 'index')
TMP_DIRECTORY = 'tmp'

if not os.path.exists(OUTPUT_DIRECTORY):
    os.mkdir(OUTPUT_DIRECTORY)

if not os.path.exists(TMP_DIRECTORY):
    os.mkdir(TMP_DIRECTORY)

tree_data = []  # menu.json
tab_dict = {}   # tabs.json
submenus = {}   # submenus.json

# output_2 = codecs.open(os.path.join(OUTPUT_DIRECTORY, sc_id + '.html'), 'w', 'utf-8')
doc_list = []  # [docid, ...]


link_subref = {}


# not implemented yet
#ids = {}   # {id: docid}
links = {}     # {linkid: id, ...}
menu_links = {}
docs_new = {}  # {id: {'menu': ?, 'tab': ?, 'doc': ?, 'anchor': ?}, ...}


for sct in soup.findAll('sct'):
    tree_data.append({
        'text': sct.find('name').contents[0],
        'selectable': False,
        'nodes': [],
    })

    for sc in sct.findAll('sc'):
        sc_id = sc['id']
        tree_data[-1]['nodes'].append({
            'text': sc.find('name').contents[0],
            'href': '#{}'.format(sc_id),
            'data-id': sc_id,
        })
        #print('\t', sc.find('name').contents[0], '({})'.format(sc_id))

        # links.setdefault(sie['docid'], {})[link['linkid']] = link['dest']
        menu_links[sc['num']] = {
            'menu': sc_id,
            # 'tab': None,
            # 'doc': None,
            # 'anchor': None,
        }

        submenus[sc_id] = {}
        for sit in sc.findAll('sit'):
            tab_dict[sit['num']] = sit.find('name').contents[0]

            submenus[sc_id][sit['num']] = []

            for sie in sit.findAll('sie'):
                doc_list.append(sie['docid'])

                docs_new[sie['id']] = {
                    'menu': sc_id,
                    'tab': sit['num'],
                    'doc': sie['docid'],
                    #'anchor': None,
                }
                #ids[sie['id']] = sie['docid']

                children = []

                # Get links
                for link in sie.find_all('link'):
                    #links.setdefault(sie['docid'], {})[link['linkid']] = link['dest']
                    if link['linkid'] in links and link['dest'] != links[link['linkid']]:
                        print('Error: Colliding link ids', link['linkid'])
                        sys.exit()
                    links[link['linkid']] = link['dest']


                for sisub in sie.find_all('sisub'):
                    #links.setdefault(sie['docid'], {})
                    link_subref[sisub['id']] = dict(docs_new[sie['id']])
                    link_subref[sisub['id']]['anchor'] = sisub['sisubid']

                    sisub_name_contents = sisub.find('name').contents  # name tag might be empty for unknown reason
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

#with open(os.path.join(OUTPUT_DIRECTORY, 'doc.json'), 'w') as outfile:
#    json.dump(docs_new, outfile)

with open(os.path.join(OUTPUT_DIRECTORY, 'menu.json'), 'w') as outfile:
    json.dump(tree_data, outfile)

tabs = []
for key, value in sorted(tab_dict.items()):
    tabs.append({
        'id': key,
        'name': value,
    })

with open(os.path.join(OUTPUT_DIRECTORY, 'tabs.json'), 'w') as outfile:
    json.dump(tabs, outfile)

with open(os.path.join(OUTPUT_DIRECTORY, 'submenus.json'), 'w') as outfile:
    json.dump(submenus, outfile)

links_new = {}
for link_id, link_dest in links.items():
    if link_dest in docs_new:
        links_new[link_id] = docs_new[link_dest]
    elif link_dest in link_subref:
        links_new[link_id] = link_subref[link_dest]
    else:
        raise Exception('Unknown destination id={}'.format(link_dest))

for link_id, dest in menu_links.items():
    if link_id in links_new:
        print('Error: Collision with menu link id')
        sys.exit()
    links_new[link_id] = dest

with open(os.path.join(OUTPUT_DIRECTORY, 'references.json'), 'w') as outfile:
    json.dump(links_new, outfile)

# Temporary files
with open(os.path.join(TMP_DIRECTORY, 'doc_list.json'), 'w') as outfile:
    json.dump(doc_list, outfile)

#with open(os.path.join(TMP_DIRECTORY, 'links.json'), 'w') as outfile:
#    json.dump(links, outfile)

#with open(os.path.join(TMP_DIRECTORY, 'link_ref.json'), 'w') as outfile:
#    json.dump(ids, outfile)

#with open(os.path.join(TMP_DIRECTORY, 'link_subref.json'), 'w') as outfile:
#    json.dump(link_subref, outfile)
