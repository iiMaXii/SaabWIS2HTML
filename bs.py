#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import htmlmin
import datetime

from bs4 import BeautifulSoup
from bs4 import Doctype
from glob import glob

DIRECTORY = 'static/data/se'
IMG_DIRECTORY = 'static/data/images'

replacements = {
    #'<SCRIPT LANGUAGE="JavaScript">GetImagePosLeft();</SCRIPT>': '<DIV style="position:absolute;left:0;top:0">',
    '<SCRIPT LANGUAGE="JavaScript">GetImagePosLeft();</SCRIPT>': '<DIV>',
    '<SCRIPT LANGUAGE="JavaScript">\n\tfunction GetIEVersion()\n\t{\n\t\tmsieIndex = navigator.appVersion.indexOf("MSIE") + 5;\n\t\tvar floatVersion = parseFloat(navigator.appVersion.substr(msieIndex,3));\n\t\treturn floatVersion;\n\t}\n\tfunction GetImagePosLeft()\n\t{\n\t\tvar IEVersion = GetIEVersion();\n\t\tif (IEVersion > 5.01)\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:-20;top:0\'>");\n\t\telse\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:0;top:0\'>");\n\t}\n\t</SCRIPT>': '',
}

img_extensions = {}
for f in os.listdir(IMG_DIRECTORY):
    if os.path.isfile(os.path.join(IMG_DIRECTORY, f)):
        filename, extension = f.rsplit('.', 1)
        img_extensions[filename] = extension

doc_files = [f for f in glob(os.path.join(DIRECTORY, "doc[0-9]*.htm"))]

img_count = 0
img_fail_count = 0
img_fail_list = []
doc_count = 0

dt_start = datetime.datetime.now()

doc_files = ['static/data/se/doc30070.htm']

for file_path in sorted(doc_files):
    doc_count += 1
    print('Processing {} ({} of {})'.format(file_path, doc_count,
                                            len(doc_files)))

    with open(file_path) as f:
        source = f.read()

    for old, new in replacements.items():
        source = source.replace(old, new)

    import re

    #warning_regex = re.compile("<TABLE bgcolor='ffdddd' border='0' style='border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;' cellspacing='0' rules='none' width='100%'><TR align='center'><TD height='60' style='color:red;font-weight:bold;font-size:10pt;font-family:Verdana;'><IMG Src='attention.gif'>&nbsp;(.*?)</TD></TR><TR><TD><TABLE width='97%' style='margin-left:5pt;'>\s+<TR><TD style='font-family:Verdana;color:black;font-size:10pt;' colspan='3'><P style='margin-bottom:5pt;'>(.*?)</P></TD></TR>\s+</TABLE></TD></TR><TR><TD height='10'></TD></TR></TABLE>")
    warning_regex = re.compile("<SPAN style='position:relative'><TABLE bgcolor='white' border='0' style='border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;' cellspacing='1' rules='none' width='60%'><TR><TD>\s+<TABLE bgcolor='white' border='0' style='border-bottom: red 3px solid; border-top: red 3px solid;border-right: red 3px solid;border-left: red 3px solid;' cellspacing='1' rules='none' width='100%'><TR><TD>\s+<TABLE bgcolor='ffdddd' border='0' style='border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;' cellspacing='0' rules='none' width='100%'><TR align='center'><TD height='60' style='color:red;font-weight:bold;font-size:10pt;font-family:Verdana;'><IMG Src='attention.gif'>&nbsp;(.*?)</TD></TR><TR><TD><TABLE width='97%' style='margin-left:5pt;'>\s+<TR><TD style='font-family:Verdana;color:black;font-size:10pt;' colspan='3'><P style='margin-bottom:5pt;'>(.*?)</P></TD></TR>\s+</TABLE></TD></TR><TR><TD height='10'></TD></TR></TABLE>\s+</TD>\s+</TR>\s+</TABLE>\s+</TD>\s+</TR>\s+</TABLE>\s+<BR>\s+</SPAN>")

    source = warning_regex.sub('<div class="alert alert-danger"><strong>\g<1></strong> \g<2></div>', source)

    soup = BeautifulSoup(source, 'html.parser')

    # Error if we find any script
    if soup.find('script'):
        print('Error: Unable to remove all script tags from {}'
              .format(file_path))
        sys.exit()

    # Replace warning img with bootstrap warning glyph icon
    for img in soup.find_all('img'):
        if img['src'] == 'attention.gif':
            glyph_icon = soup.new_tag('span')
            glyph_icon['class'] = 'glyphicon glyphicon-warning-sign'
            img.replace_with(glyph_icon)

    for link in soup.find_all('a'):
        if not link.contents:
            print('No contents in a tag. Removing')
            link.extract()
        elif link['href'].startswith('wisref://'):
            doc_id = link['href'][10:]
            link['href'] = 'javascript:void(0)'
            link['onclick'] = 'open_doc({})'.format(doc_id)
        elif link['href'].startswith('wisimg://'):
            img_count += 1
            img_id = link['href'][10:]

            extension = img_extensions.get(img_id, None)

            if not extension:
                print('Error: Unable to find image {}'.format(img_id))
                img_fail_count += 1
                img_fail_list.append(file_path)

            img_tag = soup.new_tag("img")
            img_tag['src'] = '/static/data/images/{}.{}'.format(img_id,
                                                                extension)
            img_tag['width'] = '300px'
            img_tag['alt'] = ''

            link.replace_with(img_tag)

    # Insert doctype
    img_tag = soup.new_tag("!DOCTYPE")
    doctype_tag = Doctype('html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"')
    soup.insert(0, doctype_tag)

    # Insert shit into html tag
    soup.find('html')['xmlns'] = 'http://www.w3.org/1999/xhtml'
    soup.find('head').append(soup.new_tag('title'))

    # Generate HTML source code
    html_source = str(soup)
    html_source = html_source.replace('</br>', '').replace('<br>', '<br/>')
    html_source = htmlmin.minify(html_source, remove_comments=True)

    with open('{}l'.format(file_path), 'w', encoding='utf-8') as f:
        f.write(html_source)

dt_end = datetime.datetime.now()
elapsed_seconds = (dt_end - dt_start).total_seconds()

print('Processed {} files'.format(doc_count))
if img_fail_count > 0:
    print('Failed to find {} image(s) (total {}): {}'
          .format(img_fail_count, img_count, ', '.join(img_fail_list)))

print('Execution time: {}s'.format(elapsed_seconds))
