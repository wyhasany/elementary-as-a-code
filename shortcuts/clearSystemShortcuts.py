#!/usr/bin/python3

import urllib.request
import xml.etree.ElementTree as ET

#Download default root keymap
url = 'https://raw.githubusercontent.com/JetBrains/intellij-community/282253b8ee888b51c0e8f63f44d9d4ecae9c19d2/platform/platform-resources/src/keymaps/%24default.xml'
urllib.request.urlretrieve(url, "$default.xml")
#Download XWin keymap
url = 'https://raw.githubusercontent.com/JetBrains/intellij-community/282253b8ee888b51c0e8f63f44d9d4ecae9c19d2/platform/platform-resources/src/keymaps/Default%20for%20XWin.xml'
urllib.request.urlretrieve(url, "Default for XWin.xml")

#Merge keymaps
tree_parent = ET.parse('$default.xml')
root_parent = tree_parent.getroot()

tree_child = ET.parse('Default for XWin.xml')
root_child = tree_child.getroot()

for child in root_child:
    #creates xpath to find parent xml element to overwrite
    chs = root_parent.findall('.//' + child.tag + '[@id=\'' + child.attrib['id'] + '\']')
    for x in chs:
        root_parent.remove(x)
    root_parent.append(child)

tree_parent.write("merged.xml")

#Load all idea shortcuts to array
idea_key_strokes = [ks.attrib.get('first-keystroke') for ks in tree_parent.findall('.//keyboard-shortcut')]

#For debug
for key_stroke in idea_key_strokes:
    print(key_stroke)
    # ADD -> plus
    #
