#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bs for beautiful soup the library being used, alternatively bs could mean
bullshit for the internet explorer shit code that was used to make the Saab WIS
"""

import logging
import sys
import os
import htmlmin
import datetime
import re
import json
import copy

from bs4 import BeautifulSoup
import bs4
from bs4 import Doctype
from glob import glob

from itertools import islice

LANGUAGE = 'se'
DIRECTORY = os.path.join('static', 'data', LANGUAGE)
IMG_DIRECTORY = os.path.join('static', 'data', 'images')

replacements = {
    # We probably don't need the br tags
    '<BR>': '',
    '<br>': '',

    # Some Javascript IE crap
    '<SCRIPT LANGUAGE="JavaScript">GetImagePosLeft();</SCRIPT>': '<DIV>',
    '<SCRIPT LANGUAGE="JavaScript">\n\tfunction GetIEVersion()\n\t{\n\t\tmsieIndex = navigator.appVersion.indexOf("MSIE") + 5;\n\t\tvar floatVersion = parseFloat(navigator.appVersion.substr(msieIndex,3));\n\t\treturn floatVersion;\n\t}\n\tfunction GetImagePosLeft()\n\t{\n\t\tvar IEVersion = GetIEVersion();\n\t\tif (IEVersion > 5.01)\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:-20;top:0\'>");\n\t\telse\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:0;top:0\'>");\n\t}\n\t</SCRIPT>': '',
}

# Read links
doc_list = []
links = None
link_ref = None
link_subref = None

try:
    f = open('tmp/doc_list.json')
    doc_list = json.load(f)

    f = open('tmp/links.json')
    links = json.load(f)

    f = open('tmp/link_ref.json')
    link_ref = json.load(f)

    f = open('tmp/link_subref.json')
    link_subref = json.load(f)
except (IOError, OSError) as e:
    pass

if not doc_list or not links or not link_ref or not link_subref:
    print('Error: Please run gen.py first')
    sys.exit()

ordered_list_regex = re.compile("\d+\.")

img_extensions = {}
for f in os.listdir(IMG_DIRECTORY):
    if os.path.isfile(os.path.join(IMG_DIRECTORY, f)):
        filename, extension = f.rsplit('.', 1)
        img_extensions[filename] = extension

doc_list = [16610]

#doc_files = [f for f in glob(os.path.join(DIRECTORY, "doc[0-9]*.htm"))]
doc_files = [os.path.join(DIRECTORY, 'doc{}.htm'.format(doc_id)) for doc_id in doc_list]

img_count = 0
img_fail_count = 0
img_fail_list = []
doc_count = 0

dt_start = datetime.datetime.now()

#doc_files = ['static/data/se/doc43727.htm']


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def consume(iterator, n):
    """ Advance the iterator n steps
    """
    next(islice(iterator, n, n), None)


def unwrap_and_advance(tag: bs4.Tag, iterator: iter):
    """ Unwrap a tag and advance the iterator to prevent processing of elements inside the tag
    """
    content_count = len(tag.contents)
    tag.unwrap()
    consume(iterator, content_count - 1)

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

# Meh
doc_title = None


def convert_document(soup, element):
    global doc_title

    current_list = None

    iterator = element.children
    for child in iterator:
        if isinstance(child, bs4.NavigableString):
            pass
        elif isinstance(child, bs4.Tag):
            logging.debug('Processing tag {}'.format(child.name))

            if child.name == 'table':
                if child.attrs == {'cellpadding': '0', 'bgcolor': '#6699cc', 'cellspacing': '0', 'border': '0',
                                   'style': 'margin-left:0pt;', 'width': '100%'}:
                    logging.debug('Element type: Heading')

                    if doc_title:
                        print('Error: Multiple titles for the same document')
                        sys.exit()

                    doc_title = child.tbody.tr.find_all('td', recursive=False)[1].string

                    child.name = 'h1'
                    child.attrs = {}
                    child.string = doc_title
                elif child.attrs == {'border': '0', 'width': '92%', 'style': 'margin-left:-3pt;',
                                     'cellpadding': '0', 'bgcolor': '#6699cc', 'cellspacing': '0'}:
                    logging.debug('Sub heading')

                    sub_heading = child.tbody.tr.td.string

                    child.name = 'h2'
                    child.attrs = {}
                    child.string = sub_heading
                elif child.attrs == {'rules': 'none', 'width': '60%', 'cellspacing': '1',
                                     'style': 'border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;',
                                     'border': '0', 'bgcolor': 'white'}:
                    logging.debug('Warning tag')

                    warning_table = child.table.tbody.tr.td

                    convert_document(soup, warning_table)
                    print(child.table.tbody.tr.td)

                    p_tags = warning_table.find_all('p', recursive=False)
                    print('ptags: ',p_tags)

                    p_tags[1].unwrap()
                    p_tags[0].name = 'h4'
                    p_tags[0]['class'] = ['alert-heading']

                    warning_table.name = 'div'
                    warning_table['class'] = ['alert', 'alert-danger']

                    warning_table.extract()
                    child.replace_with(warning_table)
                elif child.attrs == {'width': '60%', 'bordercolor': '#000000', 'bgcolor': 'f8f8f8', 'rules': 'none',
                                     'cellpadding': '5', 'frame': 'hsides', 'cellspacing': '0'}:
                    logging.debug('Observe tag')

                    child.attrs = {}
                    observe_tag = soup.new_tag('div')
                    observe_tag['class'] = ['alert', 'alert-warning']
                    child.wrap(observe_tag)

                    convert_document(soup, observe_tag)

                    observe_tag.contents[0].name = 'h4'
                    observe_tag.contents[0]['class'] = ['alert-heading']
                else:
                    logging.debug('Assuming general table')

                    for row in child.tbody.find_all('tr', recursive=False):
                        columns = row.find_all('td', recursive=False)
                        if len(columns) == 1:
                            columns[0].name = 'p'
                            columns[0].attrs = {}

                            convert_document(soup, columns[0])

                            row.unwrap()
                            #unwrap_and_advance(row, iterator)
                        elif len(columns) == 2:
                            left_col, right_col = columns

                            convert_document(soup, right_col)

                            if ordered_list_regex.match(left_col.string):
                                list_item_index = int(left_col.string[:-1])

                                list_item = soup.new_tag('li')
                                for c in right_col.contents:
                                    list_item.append(copy.copy(c))

                                print(list_item_index)
                                if list_item_index == 1:
                                    current_list = soup.new_tag('ol')
                                    row.replace_with(current_list)
                                elif current_list.name != 'ol':
                                    logging.error('List mismatch')
                                    sys.exit()
                                elif not current_list or len(current_list.contents) + 1 != list_item_index:
                                    logging.error('List index error')
                                    sys.exit()
                                else:
                                    row.replace_with('\n')

                                current_list.append(list_item)
                            elif left_col.string == '•':

                                list_item = soup.new_tag('li')
                                for list_content in right_col.children:
                                    list_item.append(copy.copy(list_content))

                                if current_list and current_list.name == 'ul':
                                    row.replace_with('\n')
                                else:
                                    current_list = soup.new_tag('ul')
                                    row.replace_with(current_list)

                                current_list.append(list_item)
                            else:
                                print('List with "{}", not implemented'.format(left_col.string))
                                sys.exit()

                        else:
                            logging.error('Parsing table with more than 3 columns is not implemented yet')
                            sys.exit()

                    if not child.contents:
                        child.replace_with('\n')
                    else:
                        child.tbody.unwrap()
                        unwrap_and_advance(child, iterator)
            elif child.name == 'div' or child.name == 'span' or child.name == 'p':
                child.insert(0, '\n')
                child.unwrap()
            elif child.name == 'img':
                if child['src'] == 'link.gif':
                    glyph_icon = soup.new_tag('span')
                    glyph_icon['class'] = ['glyphicon', 'glyphicon-link']
                    child.replace_with(glyph_icon)
                elif child['src'] == 'attention.gif':
                    glyph_icon = soup.new_tag('span')
                    glyph_icon['class'] = ['glyphicon', 'glyphicon-warning-sign']
                    child.replace_with(glyph_icon)
                else:
                    logging.error('Unknown image {}'.format(img['src']))
                    sys.exit()

            elif child.name == 'a':
                if not child.contents and 'name' in child.attrs:
                    if is_int(child['name']):
                        child.replace_with('\n')
                    else:
                        child.name = 'span'
                        child.attrs = {'id': child['name']}
                elif 'href' in child.attrs:
                    if child['href'].startswith('wisimg://i'):
                        # Image reference

                        img_id = child['href'][10:]
                        extension = img_extensions.get(img_id, None)

                        if not extension:
                            print('Error: Unable to find image {}'.format(img_id))

                        figure_tag = soup.new_tag('figure')

                        img_tag = soup.new_tag('img')
                        img_tag['src'] = '/static/data/images/{}.{}'.format(img_id, extension)
                        img_tag['width'] = '300'
                        img_tag['alt'] = img_id

                        figure_tag.append(img_tag)

                        # figcaption_tag = soup.new_tag('figcaption')
                        # figcaption_tag.append('caption goes here')
                        # figure_tag.append(figcaption_tag)

                        child.replace_with(figure_tag)
                    elif child['href'].startswith('wisref://c'):
                        # Menu reference

                        link_ref_id = link['href'][10:]

                        child['href'] = 'javascript:void(0)'
                        child['onclick'] = 'open_menu({})'.format(link_ref_id)
                    elif child['href'].startswith('wisref://l'):
                        # Page reference

                        link_ref_id = link['href'][10:]

                        child['href'] = 'javascript:void(0)'
                        child['onclick'] = 'open_doc({})'.format(link_ref_id)
                    else:
                        logging.error('Unknown reference ({})'.format(link['href']))
                        sys.exit()
                else:
                    logging.error('Unknown a-tag')
                    sys.exit()
            else:
                print('Error: Unknown tag {}'.format(child.name))
                print(child)
                sys.exit()

        else:
            print('Error: Unexpected bs4 element ({})'.format(type(child)))


for file_path in sorted(doc_files):
    doc_count += 1
    print('Processing {} ({} of {})'.format(file_path, doc_count,
                                            len(doc_files)))

    doc_id = os.path.splitext(os.path.basename(file_path))[0][3:]
    doc_title = None

    with open(file_path) as f:
        source = f.read()

    for old, new in replacements.items():
        source = source.replace(old, new)

    soup = BeautifulSoup(source, 'html5lib')

    # Error if we find any script
    if soup.find('script'):
        print('Error: Unable to remove all script tags from {}'.format(file_path))
        sys.exit()

    convert_document(soup, soup.body)

    for p in soup.find_all('p'):
        if p.attrs == {'style': 'margin-top:3pt;margin-bottom;10pt;'} or p.attrs == {'style': 'margin-bottom:5pt;'}:
            #del p['style']
            p.replace_with_children()

    for img in soup.find_all('img'):
        if img['src'] == 'link.gif':
            glyph_icon = soup.new_tag('span')
            glyph_icon['class'] = 'glyphicon glyphicon-link'
            img.replace_with(glyph_icon)

    # Remove span tags with style=position:relative
    for span in soup.find_all('span'):
        if span.attrs == {'style': 'position:relative'}:
            #del span['style']
            #span.name = 'p'
            span.replaceWithChildren()

    # Remove empty div tags
    for div in soup.find_all('div'):
        if not div.attrs or div.attrs == {'style': 'margin-left:20pt;margin-right:5pt;'}:
            div.replaceWithChildren()

    for link in soup.find_all('a'):
        if not link.contents:
            pass
            #print('No contents in a tag. Removing')
            #link.extract()
        elif link['href'].startswith('wisref://l'):
            # Page reference

            link_ref_id = link['href'][10:]
            if doc_id not in links:
                print('Error: Unable to find reference {} for doc{}'.format(link_ref_id, doc_id))
                continue

            link_real_ref = links[doc_id][link_ref_id]

            link['href'] = 'javascript:void(0)'

            if doc_count == 662:
                pass
            # Is this a reference to a doc
            if link_real_ref in link_ref:
                link['onclick'] = 'open_doc({})'.format(link_ref[link_real_ref])
            # Is this a reference to part of a doc
            elif link_real_ref in link_subref:
                link['onclick'] = 'open_sub_doc({}, {})'.format(link_subref[link_real_ref][0], link_subref[link_real_ref][1])
            else:
                print('Error: Unable to follow reference id={}'.format(link_real_ref))
                sys.exit()
        elif link['href'].startswith('wisref://c'):
            # Menu reference

            link_ref_id = link['href'][10:]

        elif link['href'].startswith('wisimg://'):
            img_count += 1
            img_id = link['href'][10:]

            extension = img_extensions.get(img_id, None)

            if not extension:
                print('Error: Unable to find image {}'.format(img_id))
                img_fail_count += 1
                img_fail_list.append(file_path)

            figure_tag = soup.new_tag('figure')

            img_tag = soup.new_tag('img')
            img_tag['src'] = '/static/data/images/{}.{}'.format(img_id,
                                                                extension)
            img_tag['width'] = '300'
            img_tag['alt'] = ''

            figure_tag.append(img_tag)

            #figcaption_tag = soup.new_tag('figcaption')
            #figcaption_tag.append('caption goes here')
            #figure_tag.append(figcaption_tag)

            link.replace_with(figure_tag)
        else:
            print('Warning: Unknown reference ({})'.format(link['href']))
    # Insert doctype
    img_tag = soup.new_tag("!DOCTYPE")
    doctype_tag = Doctype('html')
    soup.insert(0, doctype_tag)

    # Insert shit into html tag
    title_tag = soup.new_tag('title')
    if doc_title:
        title_tag.append(doc_title)
    soup.find('head').append(title_tag)

    del soup.find('body')['style']

    # Generate HTML source code
    html_source = soup.prettify()
    # html_source = html_source.replace('</br>', '').replace('<br>', '<br/>')

    # html_source = htmlmin.minify(html_source, remove_comments=True)

    with open('{}l'.format(file_path), 'w', encoding='utf-8') as f:
        f.write(html_source)

dt_end = datetime.datetime.now()
elapsed_seconds = (dt_end - dt_start).total_seconds()

print('Processed {} files'.format(doc_count))
if img_fail_count > 0:
    print('Failed to find {} image(s) (total {}): {}'
          .format(img_fail_count, img_count, ', '.join(img_fail_list)))

print('Execution time: {}s'.format(elapsed_seconds))
