#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
bs for beautiful soup the library being used, alternatively bs could mean
bullshit for the internet explorer shit code that was used to make the Saab WIS
"""

import sys
import os
import htmlmin
import datetime
import re

from bs4 import BeautifulSoup
from bs4 import Doctype
from glob import glob

DIRECTORY = 'static/data/se'
IMG_DIRECTORY = 'static/data/images'


replacements = {
    # We don't need BR (I think)
    '<BR>': '',
    '<br>': '',

    # Some Javascript IE crap
    '<SCRIPT LANGUAGE="JavaScript">GetImagePosLeft();</SCRIPT>': '<DIV>',
    '<SCRIPT LANGUAGE="JavaScript">\n\tfunction GetIEVersion()\n\t{\n\t\tmsieIndex = navigator.appVersion.indexOf("MSIE") + 5;\n\t\tvar floatVersion = parseFloat(navigator.appVersion.substr(msieIndex,3));\n\t\treturn floatVersion;\n\t}\n\tfunction GetImagePosLeft()\n\t{\n\t\tvar IEVersion = GetIEVersion();\n\t\tif (IEVersion > 5.01)\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:-20;top:0\'>");\n\t\telse\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:0;top:0\'>");\n\t}\n\t</SCRIPT>': '',
}

# Regular expression so we can reformat to proper HTML
warning_regex = re.compile("<TABLE bgcolor='white' border='0' style='border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;' cellspacing='1' rules='none' width='60%'><TR><TD>\s+<TABLE bgcolor='white' border='0' style='border-bottom: red 3px solid; border-top: red 3px solid;border-right: red 3px solid;border-left: red 3px solid;' cellspacing='1' rules='none' width='100%'><TR><TD>\s+<TABLE bgcolor='ffdddd' border='0' style='border-bottom: red 1px solid; border-top: red 1px solid;border-right: red 1px solid;border-left: red 1px solid;' cellspacing='0' rules='none' width='100%'><TR align='center'><TD height='60' style='color:red;font-weight:bold;font-size:10pt;font-family:Verdana;'><IMG Src='attention.gif'>&nbsp;(.*?)</TD></TR><TR><TD><TABLE width='97%' style='margin-left:5pt;'>\s+<TR><TD style='font-family:Verdana;color:black;font-size:10pt;' colspan='3'><P style='margin-bottom:5pt;'>(.*?)</P></TD></TR>\s+</TABLE></TD></TR><TR><TD height='10'></TD></TR></TABLE>\s+</TD>\s+</TR>\s+</TABLE>\s+</TD>\s+</TR>\s+</TABLE>")
observe_regex = re.compile("<TABLE frame='hsides' bordercolor='#000000' cellspacing='0' cellpadding='5' rules='none' width='60%' bgcolor='f8f8f8'><TR><TD colspan='3' height='30' style='color:blue;font-weight:bold;font-size:10pt;font-family:Verdana;'>(.*?)</TD></TR>\s+<TR><TD colspan='3' style='font-family:Verdana;color:black;font-size:10pt;'><P style='margin-bottom:5pt;'>(.*?)</P></TD></TR>\s+<TR><TD height='10' colspan='3'></TD></TR></TABLE>")
h1_regex = re.compile("<TABLE width='100%' border='0' bgcolor='#6699cc' cellspacing='0' cellpadding='0' style='margin-left:0pt;'><TR><TD style='border-bottom: black 0px solid; border-top: #99ccff 0px solid;border-right: #99ccff 0px solid;border-left: #99ccff 0px solid;font-size:12pt;color:white;font-weight:bold;padding-bottom:1px;padding-top:1px;' align='left' width='27' height='25'>&nbsp;</TD><TD style='border-bottom: black 0px solid; border-top: #99ccff 0px solid;border-right: #99ccff 0px solid;border-left: #99ccff 0px solid;font-size:10pt;color:white;font-weight:bold;padding-bottom:1px;padding-top:1px;' align='left'>(.*?)</TD></TR></TABLE>")
reference_regex = re.compile("<A NAME=\"(\d+)\"></a><a name='s(\d+)'></a>")
h2_regex = re.compile("<TABLE width='92%' border='0' bgcolor='#6699cc' cellspacing='0' cellpadding='0' style='margin-left:-3pt;'><TR><TD style='border-bottom: black 0px solid; border-top: #99ccff 0px solid;border-right: #99ccff 0px solid;border-left: #99ccff 0px solid;font-size:10pt;color:white;font-weight:bold;padding-bottom:1px;padding-top:1px;' align='left'>&nbsp;(.*?)</TD></TR></TABLE>")
h3_regex = re.compile("<H2 style='font-size:10pt;margin-top:12pt;'>(.*?)</H2>")


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

#doc_files = ['static/data/se/doc30070.htm']

# TODO view-source:http://127.0.0.1:5000/static/data/se/doc26075.html
# html tag ends before text

for file_path in sorted(doc_files):
    doc_count += 1
    print('Processing {} ({} of {})'.format(file_path, doc_count,
                                            len(doc_files)))

    doc_title = None

    with open(file_path) as f:
        source = f.read()

    for old, new in replacements.items():
        source = source.replace(old, new)

    source = warning_regex.sub('<div class="alert alert-danger"><h4 class="alert-heading">\g<1></h4><p>\g<2></p></div>', source)
    source = observe_regex.sub('<div class="alert alert-info"><h4 class="alert-heading">\g<1></h4> \g<2></div>', source)

    # Extract value for page title
    for heading in re.finditer(h1_regex, source):
        if doc_title:
            print("Warning: Found multiple headings")
        else:
            doc_title = heading.group(1)

    source = h1_regex.sub('<h1>\g<1></h1>', source)
    # Reference (always (?) before sub heading)
    source = reference_regex.sub('<span id="s\g<1>"></span>', source)
    source = h2_regex.sub('<h2>\g<1></h2>', source)
    source = h3_regex.sub('<h3>\g<1></h3>', source)


    soup = BeautifulSoup(source, 'html.parser')

    # Error if we find any script
    if soup.find('script'):
        print('Error: Unable to remove all script tags from {}'
              .format(file_path))
        sys.exit()


    # Replace warning img with bootstrap warning glyph icon (obsolete)
    #for img in soup.find_all('img'):
    #    if img['src'] == 'attention.gif':
    #        glyph_icon = soup.new_tag('span')
    #        glyph_icon['class'] = 'glyphicon glyphicon-warning-sign'
    #        img.replace_with(glyph_icon)

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

    # Insert doctype
    img_tag = soup.new_tag("!DOCTYPE")
    doctype_tag = Doctype('html')
    soup.insert(0, doctype_tag)

    # Insert shit into html tag
    #soup.find('html')['xmlns'] = 'http://www.w3.org/1999/xhtml'
    title_tag = soup.new_tag('title')
    if doc_title:
        title_tag.append(doc_title)
    soup.find('head').append(title_tag)

    del soup.find('body')['style']

    # Generate HTML source code
    html_source = str(soup)
    # html_source = html_source.replace('</br>', '').replace('<br>', '<br/>')

    #html_source = htmlmin.minify(html_source, remove_comments=True)

    with open('{}l'.format(file_path), 'w', encoding='utf-8') as f:
        f.write(html_source)

dt_end = datetime.datetime.now()
elapsed_seconds = (dt_end - dt_start).total_seconds()

print('Processed {} files'.format(doc_count))
if img_fail_count > 0:
    print('Failed to find {} image(s) (total {}): {}'
          .format(img_fail_count, img_count, ', '.join(img_fail_list)))

print('Execution time: {}s'.format(elapsed_seconds))
