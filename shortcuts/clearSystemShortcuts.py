#!/usr/bin/python3
import argparse

import urllib.request
import xml.etree.ElementTree as ET
import subprocess
import re

WHITELIST = [
    "org.gnome.desktop.wm.keybindings",
    "org.gnome.settings-daemon.plugins.media-keys",
    "org.cinnamon.desktop.keybindings",
]

# Dict to map IntellIJ keys to Linux
KEYS_REGEX_MAPPING = {
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
    "BACK_QUOTE": "grave|Above_Tab|asciitilde",  # => `,
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
    "CLOSE_BRACKET": "bracketright|braceright",  # => ],
    "OPEN_BRACKET": "bracketleft|braceleft",  # => [,
    "SEMICOLON": "semicolon|colon",
    "COMMA": "comma|less",
    "QUOTE": "quotedbl|apostrophe",  # => ",
    "ESCAPE": "Escape",
    "WINDOWS": "Super",
}


def main():
    args = get_parsed_args()
    idea_key_strokes = get_idea_key_strokes()
    gsettings_output_lines = get_system_config_from_gsettings()
    for key_stroke in idea_key_strokes:
        key_stroke_split = key_stroke.split()

        # System do not implement one key shortcuts in dconf
        if len(key_stroke_split) <= 1:
            continue

        mapped_key_stroke = map_intellij_keystrokes_to_gnome_shortcuts(key_stroke_split)
        regexp = regexp_to_get_affected_system_shortcuts(mapped_key_stroke)
        find_and_display_matching_lines(
            gsettings_output_lines, regexp, key_stroke,
            verbose=args.verbose, execute=args.execute
        )


def get_parsed_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--verbose",
        help="print more information",
        action="store_true"
    )
    parser.add_argument(
        "-e", "--execute",
        help="remove/replace shortcuts conflicting to IntellIJ IDEA",
        action="store_true"
    )
    return parser.parse_args()


def get_idea_key_strokes():
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

    # Load all idea shortcuts to array
    idea_key_strokes = [
        ks.attrib['first-keystroke']
        for ks in tree_parent.findall('.//keyboard-shortcut')
    ]
    return idea_key_strokes


def get_system_config_from_gsettings():
    gsettings_output = subprocess.run(
        "gsettings list-recursively",
        shell=True,
        stdout=subprocess.PIPE,
        universal_newlines=True
    ).stdout
    lines_filtered_using_whitelist = [
        line for line in gsettings_output.splitlines()
        if any([
            suspected_string in line
            for suspected_string in WHITELIST
        ])
    ]
    return lines_filtered_using_whitelist


def map_intellij_keystrokes_to_gnome_shortcuts(key_stroke_split):
    return [
        KEYS_REGEX_MAPPING[key.upper()] if key.upper() in KEYS_REGEX_MAPPING
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


def find_and_display_matching_lines(gsettings_output_lines, regexp, key_stroke, verbose=False, execute=False):
    lines = gsettings_output_lines
    for line in lines:
        matches = re.finditer(regexp, line, re.IGNORECASE)
        for matchNum, match in enumerate(matches):
            if verbose:
                print("Original IntellIJ shortcut: ", key_stroke)
                print(line)
                print ("Match was found at {start}-{end}: {match}".format(start=match.start(), end=match.end(),
                                                                          match=match.group()))
            group = match.group()
            if "alt" in group.lower():
                pattern = re.compile("alt", re.IGNORECASE)
                end_shortcut = pattern.sub("Super", group)
                command = " ".join(['gsettings set', line.replace(group, end_shortcut)])
            else:
                command = " ".join(['gsettings set', line.replace(group, '')])
            command = command.replace("[", '"[')
            command = command.replace("]", ']"')

            print(command)
            if execute:
                result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
                if result.returncode != 0:
                    messege = "{} enexpectedly failed. \n" \
                              "exitcode: {} \n" \
                              "stdout: {} \n" \
                              "stderr: {}".format(command, result.returncode, result.stdout, result.stderr)
                    raise RuntimeError(messege)


if __name__ == '__main__':
    main()
