#!/usr/bin/python3

import urllib.request
import xml.etree.ElementTree as ET
import subprocess
import re

url = 'https://raw.githubusercontent.com/JetBrains/intellij-community/282253b8ee888b51c0e8f63f44d9d4ecae9c19d2/platform/platform-resources/src/keymaps/%24default.xml'
default_keymappings = urllib.request.urlopen(url).read().decode("utf-8")
url = 'https://raw.githubusercontent.com/JetBrains/intellij-community/282253b8ee888b51c0e8f63f44d9d4ecae9c19d2/platform/platform-resources/src/keymaps/Default%20for%20XWin.xml'
xwin_mappings = urllib.request.urlopen(url).read().decode("utf-8")

# Merge keymaps
tree_parent = ET.ElementTree(ET.fromstring(default_keymappings))
root_parent = tree_parent.getroot()
tree_child = ET.ElementTree(ET.fromstring(xwin_mappings))
root_child = tree_child.getroot()

for child in root_child:
    # creates xpath to find parent xml element to overwrite
    chs = root_parent.findall('.//' + child.tag + '[@id=\'' + child.attrib['id'] + '\']')
    for x in chs:
        root_parent.remove(x)
    root_parent.append(child)

#Load all idea shortcuts to array
idea_key_strokes = [
    ks.attrib['first-keystroke']
    for ks in tree_parent.findall('.//keyboard-shortcut')
]

#Dict to map IntellIJ keys to Linux
keys_regex_mapping = {
    "MINUS": "minus|underscore",
    "EQUALS": "equal|plus",
    "PAGE_UP": "Page_Up",
    "PAGE_DOWN": "Page_Down",
    "HOME": "Home",
    "TAB": "Tab",
    "SPACE": "space",
    "ENTER": "Return|Enter",
    "SLASH": "slash|question",
    "BACK_SLASH": "backslash|bar",
    "PERIOD": "period|greater",
    "INSERT": "Insert",
    "CONTROL": "Ctrl|Control|Primary",
    "DIVIDE": "KP_Divide",
    "ADD": "KP_Add",
    "SUBSTRACT": "KP_Substract",
    "MULTIPLY": "KP_Multiply",
    "BACK_QUOTE": "grave|Above_Tab|asciitilde", # => `,
    "1": "1|exclam",
    "2": "2|exclam",
    "3": "3|numbersign",
    "4": "4|dollar",
    "5": "5|percent",
    "6": "6|asciicircum",
    "7": "7|ampersand",
    "8": "8|asterisk",
    "9": "9|parenleft",
    "0": "0|parenright",
    "BACK_SPACE": "BackSpace",
    "DELETE": "Delete",
    "UP": "Up",
    "DOWN": "Down",
    "LEFT": "Left",
    "RIGHT": "Right",
    "CLOSE_BRACKET": "bracketright|braceright", # => ],
    "OPEN_BRACKET": "bracketleft|braceleft", # => [,
    "SEMICOLON": "semicolon|colon",
    "COMMA": "comma|less",
    "QUOTE": "quotedbl|apostrophe", # => ",
    "ESCAPE": "Escape",
    "WINDOWS": "Super",
}

#Load your system configuration
gsettings_output = subprocess.run(
    "gsettings list-recursively",
    shell=True,
    stdout=subprocess.PIPE,
    universal_newlines=True
).stdout


def map_intellij_keystrokes_to_gnome_shortcuts():
    return [
        keys_regex_mapping[key.upper()] if key.upper() in keys_regex_mapping
        else key.upper()
        for key in key_stroke_split
    ]


def regexp_to_get_affected_system_shortcuts(mapped_key_stroke):
    """
    Create regexp to get affected system shortcuts
    like this one:
    (?=.*?(control|ctrl))(?=.*?shift)'<?(shift|control|ctrl)\>?\s*<?(shift|control|ctrl)\>?\s*'
    for better understanding that regexp, check:
    https://regex101.com/r/pC8vD4/46
    """
    regexp = ""
    for key in mapped_key_stroke:
        regexp += "(?=.*?(" + key + "))"
    regexp += "'"
    for key in mapped_key_stroke:
        regexp += "<?("
        regexp += "|".join(mapped_key_stroke)
        regexp += ")\>?\s*"
    regexp += "'"
    return regexp


def find_matching_lines():
    lines = gsettings_output.splitlines()
    for line in lines:
        matches = re.finditer(regexp, line, re.IGNORECASE)
        for matchNum, match in enumerate(matches):
            print("Original IntellIJ shortcut: ", key_stroke)
            print(line)
            print ("Match was found at {start}-{end}: {match}".format(start=match.start(), end=match.end(),
                                                                      match=match.group()))

            group = match.group()
            if "alt" in group.lower():
                pattern = re.compile("alt", re.IGNORECASE)
                end_shortcut = pattern.sub("Super", group)
                print('gsettings set', line.replace(group, end_shortcut))
            else:
                print('gsettings set', line.replace(group, ''))


#Remove affected system shortcuts
for key_stroke in idea_key_strokes:
    key_stroke_split = key_stroke.split()

    #System do not implement one key shortcuts in dconf
    if len(key_stroke_split) <= 1:
        continue

    mapped_key_stroke = map_intellij_keystrokes_to_gnome_shortcuts()
    regexp = regexp_to_get_affected_system_shortcuts(mapped_key_stroke)
    find_matching_lines()


