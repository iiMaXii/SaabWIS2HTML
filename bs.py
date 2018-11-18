""" This file converts all relevant HTML documents on the Saab WIS CD to HTML5
documents.
"""

import logging
import sys
import os
# import htmlmin
import datetime
import re
import json

import bs4


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class StackElement:
    def __init__(self, level: int, element: bs4.Tag):
        self.level = level
        self.element = element


TMP_DIRECTORY = 'tmp'
LANGUAGE = 'se'
DIRECTORY = os.path.join('static', 'data', LANGUAGE)
IMG_DIRECTORY = os.path.join('static', 'data', 'images')

if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

replacements = {
    # We probably don't need the br tags
    '<BR>': '',  # TODO, maybe preserve br-tags or make two br-tags a p-tag
    '<br>': '',

    # Some Javascript IE crap
    '<SCRIPT LANGUAGE="JavaScript">GetImagePosLeft();</SCRIPT>': '<DIV>',
    '<SCRIPT LANGUAGE="JavaScript">\n\tfunction GetIEVersion()\n\t{\n\t\tmsieIndex = navigator.appVersion.indexOf("MSIE") + 5;\n\t\tvar floatVersion = parseFloat(navigator.appVersion.substr(msieIndex,3));\n\t\treturn floatVersion;\n\t}\n\tfunction GetImagePosLeft()\n\t{\n\t\tvar IEVersion = GetIEVersion();\n\t\tif (IEVersion > 5.01)\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:-20;top:0\'>");\n\t\telse\n\t\t\tdocument.write("<DIV style=\'position:absolute;left:0;top:0\'>");\n\t}\n\t</SCRIPT>': '',
}

ordered_list_regex = re.compile("\d+\.")
ordered_list_alpha_regex = re.compile("[a-z]\.")
ordered_list_number_alpha_regex = re.compile("\d+\.[A-Za-z]\.")
ordered_list_number_number_regex = re.compile("\d+\.\d+\.")

# Read links
doc_list = []
# links = None
# link_ref = None
# link_subref = None

try:
    f = open('tmp/doc_list.json')
    doc_list = json.load(f)

    """f = open('tmp/links.json')
    links = json.load(f)

    f = open('tmp/link_ref.json')
    link_ref = json.load(f)

    f = open('tmp/link_subref.json')
    link_subref = json.load(f)"""
except (IOError, OSError) as e:
    pass

if not doc_list:  # or not links or not link_ref or not link_subref:
    print('Error: Please run gen.py first')
    sys.exit()

img_extensions = {}
for f in os.listdir(IMG_DIRECTORY):
    if os.path.isfile(os.path.join(IMG_DIRECTORY, f)):
        filename, extension = f.rsplit('.', 1)
        img_extensions[filename] = extension

doc_list = doc_list[doc_list.index('42844'):]
# doc_list = [42844]

#doc_files = [os.path.join(DIRECTORY, 'doc{}.htm'.format(doc_id)) for doc_id in doc_list]
doc_files = os.listdir(os.path.join(TMP_DIRECTORY, LANGUAGE))
#doc_files = ['doc43058.htm']

# Global variables for parsing
img_count = 0
img_fail_count = 0
img_fail_list = []
doc_count = 0

doc_title = None

element_stack = []  # Lists and tables
level_count = 0


def convert_document2(input_tag: bs4.Tag, output_tag: bs4.Tag, output_soup: bs4.BeautifulSoup) -> None:
    global doc_title, element_stack, level_count

    level_count += 1
    logging.debug('level_count={}'.format(level_count))

    logging.debug('Looping {}'.format(input_tag.name))
    for input_child in input_tag.contents:
        logging.debug('Processing {} ({})'.format(input_child.name, input_child))
        if isinstance(input_child, bs4.NavigableString):
            logging.debug('Appending string "{}"'.format(str(input_child)))
            output_tag.append(str(input_child))
        elif isinstance(input_child, bs4.Comment):
            logging.debug('Skipping comment')
        elif isinstance(input_child, bs4.Tag):
            logging.debug(input_child.attrs)
            if input_child.name == 'div' or input_child.name == 'span' or input_child.name == 'p':
                convert_document2(input_child, output_tag, output_soup)
            elif (input_child.name == 'i' or input_child.name == 'b' or input_child.name == 'sup'
                  or input_child.name == 'sub' or input_child.name == 'u'):
                # TODO maybe replace <u> with <span style="text-decoration:underline;">
                tag = output_soup.new_tag(input_child.name)
                output_tag.append(tag)
                convert_document2(input_child, tag, output_soup)
            elif input_child.name == 'h2':
                h3_tag = output_soup.new_tag('h3')
                convert_document2(input_child, h3_tag, output_soup)
                output_tag.append(h3_tag)
            elif input_child.name == 'meta':
                if input_child.attrs == {'http-equiv': 'Content-Type', 'content': 'text/html; charset=windows-1252'}:
                    pass  # Ignore
                else:
                    logging.error('Unknown meta tag attributes')
                    sys.exit()
            elif input_child.name == 'input':
                if input_child.attrs == {'type': 'checkbox'}:
                    checkbox = output_soup.new_tag('input')
                    checkbox.attrs = {'type': 'checkbox'}
                else:
                    logging.error('Unexpected input tag')
                    sys.exit()
            elif input_child.name == 'table':
                if input_child.attrs == {'cellpadding': '0', 'bgcolor': '#6699cc', 'cellspacing': '0', 'border': '0',
                                         'style': 'margin-left:0pt;', 'width': '100%'}:
                    logging.debug('Processing heading table')

                    if doc_title:
                        logging.error('Error: Multiple titles for the same document')
                        sys.exit()

                    if (len(input_child.tbody.find_all('tr', recursive=False)) != 1 or
                            len(input_child.tbody.tr.find_all('td', recursive=False)) != 2):
                        logging.error('Unexpected tr/td count')
                        sys.exit()

                    input_title_content = input_child.tbody.tr.find_all('td', recursive=False)[1]

                    h1_tag = output_soup.new_tag('h1')
                    convert_document2(input_title_content, h1_tag, output_soup)

                    doc_title = h1_tag.string
                    if not doc_title:
                        doc_title = ''
                        for t in h1_tag:
                            if isinstance(t, bs4.NavigableString):
                                doc_title += t.string

                    logging.debug('title={}'.format(doc_title))
                elif input_child.attrs == {'border': '0', 'width': '92%', 'style': 'margin-left:-3pt;',
                                           'cellpadding': '0', 'bgcolor': '#6699cc', 'cellspacing': '0'}:
                    logging.debug('Sub heading')

                    if (len(input_child.tbody.find_all('tr', recursive=False)) != 1 or
                            len(input_child.tbody.tr.find_all('td', recursive=False)) != 1):
                        logging.error('Unexpected tr/td count')
                        sys.exit()

                    h2_tag = output_soup.new_tag('h2')
                    # TODO remove <b> element? (e.g. in doc33205.htm)
                    convert_document2(input_child.tbody.tr.td, h2_tag, output_soup)

                    output_tag.append(h2_tag)
                elif input_child.attrs == {'rules': 'none', 'width': '60%', 'cellspacing': '1',
                                           'style': ('border-bottom: red 1px solid; border-top: red 1px solid;'
                                                     'border-right: red 1px solid;border-left: red 1px solid;'),
                                           'border': '0', 'bgcolor': 'white'}:
                    logging.debug('Warning tag')

                    warning_tag = output_soup.new_tag('div')
                    warning_tag['class'] = ['alert', 'alert-danger']

                    logging.debug('Entering warning')
                    tr_tags = input_child.table.table.tbody.find_all('tr', recursive=False)
                    if len(tr_tags) != 3:
                        logging.error('Warning tag tr count missmatch')
                        sys.exit()

                    title_input_tags = tr_tags[0].find_all('td', recursive=False)
                    if len(title_input_tags) != 1:
                        logging.error('Warning tag title td count missmatch')
                        sys.exit()

                    contents_input_tags = tr_tags[1].find_all('td', recursive=False)
                    if len(contents_input_tags) != 1:
                        logging.error('Warning tag contents td count missmatch')
                        sys.exit()

                    heading_tag = output_soup.new_tag('h4')
                    heading_tag.attrs = {'class': ['alert-heading']}
                    convert_document2(title_input_tags[0], heading_tag, output_soup)
                    warning_tag.append(heading_tag)

                    convert_document2(contents_input_tags[0], warning_tag, output_soup)

                    logging.debug('Leaving warning')

                    output_tag.append(warning_tag)

                elif input_child.attrs == {'width': '60%', 'bordercolor': '#000000', 'bgcolor': 'f8f8f8',
                                           'rules': 'none', 'cellpadding': '5', 'frame': 'hsides', 'cellspacing': '0'}:
                    logging.debug('Observe tag')

                    observe_tag = output_soup.new_tag('div')
                    observe_tag['class'] = ['alert', 'alert-warning']

                    convert_document2(input_child, observe_tag, output_soup)

                    heading_tag = observe_tag.p
                    heading_tag.name = 'h4'
                    heading_tag.attrs = {'class': ['alert-heading']}

                    output_tag.append(observe_tag)
                elif input_child.attrs == {'rules': 'none', 'bgcolor': 'f8f8f8', 'frame': 'void', 'width': '60%'}:
                    logging.debug('Note tag')

                    note_tag = output_soup.new_tag('div')
                    note_tag['class'] = ['alert', 'alert-info']

                    convert_document2(input_child, note_tag, output_soup)

                    heading_tag = note_tag.p
                    heading_tag.name = 'h4'
                    heading_tag.attrs = {'class': ['alert-heading']}

                    output_tag.append(note_tag)
                else:
                    logging.debug('General table')

                    convert_document2(input_child, output_tag, output_soup)

            elif input_child.name == 'colgroup':

                table_tag = output_soup.new_tag('table')
                colgroup_tag = output_soup.new_tag('colgroup')

                for col in input_child.find_all('col', recursive=False):
                    if 'width' not in col.attrs:
                        logging.error('Width attribute not in col')
                        sys.exit()

                    if len(col.attrs) != 1:
                        logging.error('Col attribute length mismatch')
                        sys.exit()

                    col_tag = output_soup.new_tag('col')
                    col_tag.attrs = {'style': 'width:{}'.format(col['width'])}
                    colgroup_tag.append(col_tag)

                table_tag.append(colgroup_tag)
                table_tag.append(output_soup.new_tag('tbody'))
                output_tag.append(table_tag)

                element_stack.append(StackElement(level_count, table_tag))
            elif input_child.name == 'tbody':
                logging.debug('Processing tbody')

                current_list = None
                if element_stack and element_stack[-1].level == level_count:
                    current_list = element_stack[-1].element

                for row in input_child.find_all('tr', recursive=False):
                    columns = row.find_all('td', recursive=False)

                    # Level just for extra sanity
                    indentation_level = 0
                    if columns and not columns[0].contents:
                        indentation_level = 1  # TODO levels deeper?

                    if len(columns) == 2 and columns[0].string and ordered_list_regex.match(columns[0].string):
                        # Ordered list (123...)
                        logging.debug('Ordered list')
                        left_col, right_col = columns

                        if indentation_level != 0:
                            logging.error('Indentation for ordered list is not implemented')
                            sys.exit()

                        list_item = output_soup.new_tag('li')

                        convert_document2(right_col, list_item, output_soup)

                        list_item_index = int(left_col.string[:-1])

                        if list_item_index == 1:
                            current_list = output_soup.new_tag('ol')
                            output_tag.append(current_list)
                            element_stack.append(StackElement(level_count, current_list))
                        elif current_list and (current_list.name != 'ol' or 'style' in current_list.attrs):
                            logging.error('List mismatch')
                            sys.exit()
                        elif not current_list or len(current_list.contents) + 1 != list_item_index:
                            logging.error('List index error')
                            sys.exit()

                        current_list.append(list_item)
                    elif len(columns) == 2 and columns[0].string == '•':
                        # Unordered list (•)
                        left_col, right_col = columns

                        if indentation_level != 0:
                            logging.error('Indentation for unordered list is not implemented')
                            sys.exit()

                        list_item = output_soup.new_tag('li')

                        convert_document2(right_col, list_item, output_soup)

                        if current_list and current_list.name == 'ul':
                            pass
                        else:
                            current_list = soup.new_tag('ul')
                            output_tag.append(current_list)
                            element_stack.append(StackElement(level_count, current_list))

                        current_list.append(list_item)
                    elif len(columns) == 3 and columns[1].string and columns[1].string == '•':
                        # Unordered sublist (•)
                        _, left_col, right_col = columns

                        if indentation_level == 0:
                            logging.error('No indentation for unordered sublist')
                            sys.exit()

                        if not current_list:
                            logging.error('No parent list for unordered sublist')
                            sys.exit()

                        if not current_list.contents:
                            logging.error('Empty parent list for unordered sublist')
                            sys.exit()

                        last_element = current_list.contents[-1]
                        if (not last_element.contents or last_element.contents[-1].name != 'ul'
                                or last_element.contents[-1].attrs != {'style': "list-style-type:circle"}):
                            sublist = output_soup.new_tag('ul')
                            sublist.attrs = {'style': "list-style-type:circle"}

                            last_element.append(sublist)
                        else:
                            sublist = last_element.contents[-1]

                        sublist_item = output_soup.new_tag('li')
                        convert_document2(right_col, sublist_item, output_soup)
                        sublist.append(sublist_item)
                    elif len(columns) == 3 and columns[1].string and columns[1].string == '-':
                        # Unordered sublist (-)
                        _, left_col, right_col = columns

                        if indentation_level == 0:
                            logging.error('No indentation for unordered sublist')
                            sys.exit()

                        if not current_list:
                            logging.error('No parent list for unordered sublist')
                            sys.exit()

                        if not current_list.contents:
                            logging.error('Empty parent list for unordered sublist')
                            sys.exit()

                        last_element = current_list.contents[-1]
                        if (not last_element.contents or last_element.contents[-1].name != 'ul'
                                or last_element.contents[-1].attrs != {'style': "list-style-type:'-  '"}):
                            sublist = output_soup.new_tag('ul')
                            sublist.attrs = {'style': "list-style-type:'-  '"}

                            last_element.append(sublist)
                        else:
                            sublist = last_element.contents[-1]

                        sublist_item = output_soup.new_tag('li')
                        convert_document2(right_col, sublist_item, output_soup)
                        sublist.append(sublist_item)
                    elif len(columns) == 3 and columns[1].string and ordered_list_alpha_regex.match(columns[1].string):
                        # Ordered sublist (abc...)
                        _, left_col, right_col = columns

                        if indentation_level == 0:
                            logging.error('No indentation for ordered sublist')
                            sys.exit()

                        if not current_list:
                            logging.error('No parent list for unordered sublist')
                            sys.exit()

                        if not current_list.contents:
                            logging.error('Empty parent list for unordered sublist')
                            sys.exit()

                        last_element = current_list.contents[-1]
                        if (not last_element.contents or last_element.contents[-1].name != 'ol'
                                or last_element.contents[-1].attrs != {'style': 'list-style-type:lower-alpha'}):
                            sublist = output_soup.new_tag('ol')
                            sublist.attrs = {'style': 'list-style-type:lower-alpha'}

                            last_element.append(sublist)
                        else:
                            sublist = last_element.contents[-1]

                        sublist_item = output_soup.new_tag('li')
                        convert_document2(right_col, sublist_item, output_soup)
                        sublist.append(sublist_item)
                    elif (len(columns) == 3 and columns[1].string
                          and ordered_list_number_alpha_regex.match(columns[1].string)):
                        # Ordered sublist (1.a 2.b 1.c...)
                        _, left_col, right_col = columns

                        if indentation_level == 0:
                            logging.error('No indentation for ordered sublist')
                            sys.exit()

                        if not current_list:
                            logging.error('No parent list for ordered sublist')
                            sys.exit()

                        if not current_list.contents:
                            logging.error('Empty parent list for ordered sublist')
                            sys.exit()

                        last_element = current_list.contents[-1]
                        if (not last_element.contents or last_element.contents[-1].name != 'ol'
                                or last_element.contents[-1].attrs != {'style': 'list-style-type:lower-alpha'}):
                            sublist = output_soup.new_tag('ol')
                            sublist.attrs = {'style': 'list-style-type:lower-alpha'}

                            last_element.append(sublist)
                        else:
                            sublist = last_element.contents[-1]

                        sublist_item = output_soup.new_tag('li')
                        convert_document2(right_col, sublist_item, output_soup)
                        sublist.append(sublist_item)
                    elif (len(columns) == 3 and columns[1].string
                          and ordered_list_number_number_regex.match(columns[1].string)):
                        # Ordered sublist (1.1 1.2 1.3...)
                        _, left_col, right_col = columns

                        if indentation_level == 0:
                            logging.error('No indentation for ordered sublist')
                            sys.exit()

                        if not current_list:
                            logging.error('No parent list for unordered sublist')
                            sys.exit()

                        if not current_list.contents:
                            logging.error('Empty parent list for ordered sublist')
                            sys.exit()

                        last_element = current_list.contents[-1]
                        if (not last_element.contents or last_element.contents[-1].name != 'ol'
                                or last_element.contents[-1].attrs != {'style': 'list-style-type:decimal'}):
                            sublist = output_soup.new_tag('ol')
                            sublist.attrs = {'style': 'list-style-type:decimal'}

                            last_element.append(sublist)
                        else:
                            sublist = last_element.contents[-1]

                        sublist_item = output_soup.new_tag('li')
                        convert_document2(right_col, sublist_item, output_soup)
                        sublist.append(sublist_item)
                    elif len(columns) == 1 and 'rowspan' not in columns[0].attrs:
                        if output_tag.name == 'p':
                            # Prevent nesting of p-tags
                            # TODO maybe we should remove the p-tag in output instead
                            convert_document2(columns[0], output_tag, output_soup)
                        else:
                            p_tag = output_soup.new_tag('p')
                            convert_document2(columns[0], p_tag, output_soup)
                            if p_tag.contents:
                                output_tag.append(p_tag)
                    else:
                        # Normal table (N columns)
                        if indentation_level != 0:
                            logging.error('Unexpected indentation for table')
                            sys.exit()

                        if current_list and current_list.name != 'table':
                            element_stack.pop()
                            current_list = None

                        if not current_list:
                            current_list = output_soup.new_tag('table')
                            current_list.append(output_soup.new_tag('tbody'))
                            output_tag.append(current_list)
                            element_stack.append(StackElement(level_count, current_list))

                        tr_tag = output_soup.new_tag('tr')

                        for col in columns:
                            td_tag = output_soup.new_tag('td')

                            convert_document2(col, td_tag, output_soup)
                            colspan = col.attrs.get('colspan', '1')
                            rowspan = col.attrs.get('rowspan', '1')

                            if colspan != '1':
                                td_tag['colspan'] = colspan
                            if rowspan != '1':
                                td_tag['rowspan'] = rowspan

                            tr_tag.append(td_tag)

                        current_list.tbody.append(tr_tag)
            elif input_child.name == 'a':
                if not input_child.contents and 'name' in input_child.attrs:
                    if is_int(input_child['name']):
                        logging.debug('Skipping section tag "{}"'.format(input_child['name']))
                    else:
                        logging.debug('Appending section tag "{}"'.format(input_child['name']))
                        section_tag = output_soup.new_tag('span')
                        section_tag.attrs = {'id': input_child['name']}
                        output_tag.append(section_tag)
                elif 'href' in input_child.attrs:
                    if input_child['href'].startswith('wisimg://i'):
                        # Image reference

                        img_id = input_child['href'][10:]
                        extension = img_extensions.get(img_id, None)

                        if not img_id:
                            logging.warning('Broken image reference')
                            # TODO
                            """
                            <div class="broken-image-ref">
                              <span class="broken-image-ref-icon glyphicon glyphicon glyphicon-ban-circle"></span>
                              <div class="broken-image-ref-description">
                                <i>Broken image reference</i>
                              </div>
                            </div>
                            .broken-image-ref {
                              width: 300px;
                              height: 300px;
                              border: 1px solid black;
                              position: relative;
                            }
                            
                            .broken-image-ref-icon {
                              font-size: 100px;
                              width: 75px;
                              height: 75px;
                              position: absolute;
                              top: 50%;
                              left: 50%;
                              margin: -50px 0 0 -50px;
                            }
                            
                            .broken-image-ref-description {
                              width:100%;
                              position: absolute;
                              bottom: 0;
                              left: 0;
                              text-align:center;
                            }
                            """

                        elif not extension:
                            logging.error('Error: Unable to find image {}'.format(img_id))
                            sys.exit()

                        figure_tag = output_soup.new_tag('figure')

                        img_tag = output_soup.new_tag('img')
                        img_tag['src'] = '/static/data/images/{}.{}'.format(img_id, extension)
                        img_tag['width'] = '300'
                        img_tag['alt'] = img_id

                        figure_tag.append(img_tag)

                        # figcaption_tag = soup.new_tag('figcaption')
                        # figcaption_tag.append('caption goes here')
                        # figure_tag.append(figcaption_tag)

                        output_tag.append(figure_tag)
                    elif input_child['href'].startswith('wisref://c'):
                        # Menu reference

                        link_ref_id = input_child['href'][10:]
                        print('link ref: ', link_ref_id)
                        menu_reference_tag = output_soup.new_tag('a')
                        menu_reference_tag['href'] = '/{}'.format(link_ref_id)
                        menu_reference_tag['class'] = ['doc-ref']

                        output_tag.append(menu_reference_tag)
                        convert_document2(input_child, menu_reference_tag, output_soup)
                    elif input_child['href'].startswith('wisref://l'):
                        # Page reference

                        link_ref_id = input_child['href'][10:]

                        page_reference_tag = output_soup.new_tag('a')
                        page_reference_tag['href'] = '/{}'.format(link_ref_id)
                        page_reference_tag['class'] = ['doc-ref']

                        output_tag.append(page_reference_tag)
                        convert_document2(input_child, page_reference_tag, output_soup)
                    else:
                        logging.error('Unknown reference ({})'.format(input_child['href']))
                        sys.exit()
            elif input_child.name == 'img':
                if input_child['src'] == 'link.gif' or input_child['src'] == 'sclink.gif':
                    glyph_icon = output_soup.new_tag('span')
                    glyph_icon['class'] = ['glyphicon', 'glyphicon-link']
                    output_tag.append(glyph_icon)
                elif input_child['src'] == 'attention.gif':
                    glyph_icon = output_soup.new_tag('span')
                    glyph_icon['class'] = ['glyphicon', 'glyphicon-warning-sign']
                    output_tag.append(glyph_icon)
                elif input_child['src'] == 'FSanim3.gif':
                    pass  # TODO
                else:
                    logging.error('Unknown image {}'.format(input_child['src']))
                    sys.exit()
            else:
                logging.error('Unknown tag "{}"'.format(input_child.name))
                sys.exit()
        else:
            logging.error('Unknown element type "{}"'.format(type(input_child)))
            sys.exit()

    level_count -= 1

    # Clear element_stack
    new_element_stack = []
    for e in element_stack:
        if e.level - 3 <= level_count:
            new_element_stack.append(e)
        else:
            logging.debug('Removing element_stack')

    element_stack = new_element_stack

# Initiation
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

dt_start = datetime.datetime.now()

for file in sorted(doc_files):
    file_path = os.path.join(TMP_DIRECTORY, LANGUAGE, file)
    doc_count += 1
    print('Processing {} ({} of {})'.format(file_path, doc_count, len(doc_files)))

    if os.path.isfile(os.path.join(DIRECTORY, '{}l'.format(file))):
        print('File found, skipping')
        continue

    doc_id = os.path.splitext(os.path.basename(file_path))[0][3:]
    doc_title = None

    with open(file_path) as f:
        source = f.read()

    for old, new in replacements.items():
        source = source.replace(old, new)

    soup = bs4.BeautifulSoup(source, 'html5lib')

    # Error if we find any script tag
    if soup.find('script'):
        logging.error('Error: Unable to remove all script tags from {}'.format(file_path))
        sys.exit()

    output = bs4.BeautifulSoup(features='html5lib')

    # Insert doctype
    doctype_tag = bs4.Doctype('html')
    output.insert(0, doctype_tag)

    # Set language
    output.html['lang'] = LANGUAGE

    # Set charset
    meta_tag = output.new_tag('meta')
    meta_tag.attrs = {'charset': 'utf-8'}
    output.head.append(meta_tag)

    # Add bootstrap css
    link_tag = output.new_tag('link')
    link_tag['rel'] = 'stylesheet'
    link_tag['href'] = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
    link_tag['integrity'] = 'sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u'
    link_tag['crossorigin'] = 'anonymous'
    output.head.append(link_tag)

    convert_document2(soup.body, output.body, output)

    # Insert shit into html tag
    title_tag = soup.new_tag('title')
    if doc_title:
        title_tag.append(doc_title)
    output.find('head').append(title_tag)

    # Generate HTML source code
    html_source = output.prettify()

    # To make the HTML5 valid
    html_source = html_source.replace('</col>', '')

    # html_source = htmlmin.minify(html_source, remove_comments=True)

    with open(os.path.join(DIRECTORY, '{}l'.format(file)), 'w', encoding='utf-8') as f:
        f.write(html_source)

dt_end = datetime.datetime.now()
elapsed_seconds = (dt_end - dt_start).total_seconds()

print('Processed {} files'.format(doc_count))
if img_fail_count > 0:
    print('Failed to find {} image(s) (total {}): {}'.format(img_fail_count, img_count, ', '.join(img_fail_list)))

print('Execution time: {}s'.format(elapsed_seconds))
