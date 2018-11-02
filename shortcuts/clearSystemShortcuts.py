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
    "MINUS": ["MINUS", "UNDERSCORE"],
    "EQUALS": ["EQUAL", "PLUS"],
    "PAGE_UP": ["PAGE_UP"],
    "PAGE_DOWN": ["PAGE_DOWN"],
    "HOME": ["HOME"],
    "TAB": ["TAB"],
    "SPACE": ["SPACE"],
    "ENTER": ["RETURN", "ENTER"],
    "SLASH": ["SLASH", "QUESTION"],
    "BACK_SLASH": ["BACKSLASH", "BAR"],
    "PERIOD": ["PERIOD", "GREATER"],
    "INSERT": ["INSERT"],
    "CONTROL": ["CTRL", "CONTROL", "PRIMARY"],
    "DIVIDE": ["KP_DIVIDE"],
    "ADD": ["KP_ADD"],
    "SUBSTRACT": ["KP_SUBSTRACT"],
    "MULTIPLY": ["KP_MULTIPLY"],
    "BACK_QUOTE": ["GRAVE", "ABOVE_TAB", "ASCIITILDE"],  # => `,
    "1": ["1", "EXCLAM"],
    "2": ["2", "EXCLAM"],
    "3": ["3", "NUMBERSIGN"],
    "4": ["4", "DOLLAR"],
    "5": ["5", "PERCENT"],
    "6": ["6", "ASCIICIRCUM"],
    "7": ["7", "AMPERSAND"],
    "8": ["8", "ASTERISK"],
    "9": ["9", "PARENLEFT"],
    "0": ["0", "PARENRIGHT"],
    "BACK_SPACE": ["BACKSPACE"],
    "DELETE": ["DELETE"],
    "UP": ["UP"],
    "DOWN": ["DOWN"],
    "LEFT": ["LEFT"],
    "RIGHT": ["RIGHT"],
    "CLOSE_BRACKET": ["BRACKETRIGHT", "BRACERIGHT"],  # => ],
    "OPEN_BRACKET": ["BRACKETLEFT", "BRACELEFT"],  # => [,
    "SEMICOLON": ["SEMICOLON", "COLON"],
    "COMMA": ["COMMA", "LESS"],
    "QUOTE": ["QUOTEDBL", "APOSTROPHE"],  # => ",
    "ESCAPE": ["ESCAPE"],
    "WINDOWS": ["SUPER"],
}


def main():
    args = get_parsed_args()
    idea_key_strokes = get_idea_key_strokes()
    gsettings_output_lines = get_system_config_from_gsettings()
    all_commands = []
    for key_stroke in idea_key_strokes:
        if len(key_stroke.split()) <= 1:  # System do not implement one key shortcuts in dconf
            continue
        pairs = find_matching_line_keystroke_pairs(
            gsettings_output_lines, key_stroke,
            partials=args.partials, verbose=args.verbose
        )
        commands = generate_clearing_commands(pairs)
        all_commands.extend(commands)
    display(all_commands)
    if args.execute:
        execute_commands(all_commands)


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
    parser.add_argument(
        "-p", "--partials",
        help="consider system shortcuts partially covering IntellIJ IDEA as conflicting.\n"
             "For example in case of flag added <alt><s> will be considered as covering <control><alt><s>.",
        action="store_true"
    )
    return parser.parse_args()


def display(commands):
    print("Commands for clearing system shortcuts: ")
    for command in commands:
        print(command)


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
        'gsettings list-recursively | grep -v -E "\[\s*\]"',
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


def map_intellij_keystrokes_to_gnome_shortcuts(key_stroke):
    return [
        KEYS_REGEX_MAPPING.setdefault(key.upper(), [key.upper()])
        for key in key_stroke.split()
    ]


def find_matching_line_keystroke_pairs(lines, key_stroke, partials=False, verbose=False):
    result = []
    mapped_key_stroke = map_intellij_keystrokes_to_gnome_shortcuts(key_stroke)
    for line in lines:
        upper_line = line.upper()
        matches = re.finditer('\'.+?\'', upper_line)
        for match in matches:
            system_keystroke = match.group()
            if not covers(mapped_key_stroke, system_keystroke, partial_coverage_checking=partials):
                continue
            if verbose:
                print("Original IntellIJ shortcut: ", key_stroke)
                print(line)
                template = "Match was found at {start}-{end}: {match}"
                print (template.format(start=match.start(), end=match.end(), match=system_keystroke))
            result.append((line, system_keystroke))
    return result


def covers(mapped_key_stroke, system_keystroke, partial_coverage_checking=False):
    """
    Checks if system keystroke covers IDEA keystroke.
    :param mapped_key_stroke: List of possible expression for every key in IntellIJ IDEA keystroke.
            Example: [['CTRL', 'CONTROL', 'PRIMARY], ['ALT'], ['S']]
    :param system_keystroke: String representing keystroke returned by gsettings.
            Example: '<CONTROL><ALT>S'
    :param partial_coverage_checking: if true keystrokes shorter than IDEA keystrokes are also considered as covering.
            For example in case of true <alt><s> will be considered as covering <control><alt><s>.
    :return: True if system_keystroke covers IDEA keystroke, false otherwise.
    """
    ignored_characters = "<>\\\'\""
    for char in ignored_characters:
        system_keystroke = system_keystroke.replace(char, " ")  # after loop:  system_keystroke = ' CONTROL  ALT S'
    keys_list = system_keystroke.split()                        # after split: keys_list = ['CONTROL', 'ALT', 'S']

    if not partial_coverage_checking and len(mapped_key_stroke) != len(keys_list):
        return False

    condition = all([                                           # Read comments and lines following the numbers :)
        any([
            key in key_expressions                              # 2. key is a one of possible expressions ex. CTRL in ['CTRL', 'CONTROL', 'PRIMARY]
            for key_expressions in mapped_key_stroke            # 3. of a some key in IDEA keystroke
        ])
        for key in keys_list                                    # 1. for every key in system shortcut
    ])
    return condition


def generate_clearing_command(line, keystroke):
    if "ALT" in keystroke.upper():
        original_keystroke = re.findall(keystroke, line, re.IGNORECASE)[0]
        pattern = re.compile("alt", re.IGNORECASE)
        end_shortcut = pattern.sub("Super", original_keystroke)
        setting = replace_case_insensitive(line, keystroke, end_shortcut)
        command = " ".join(['gsettings set', setting])
    else:
        command = " ".join(['gsettings set', replace_case_insensitive(line, keystroke, '')])
    command = command.replace("[", '"[')
    command = command.replace("]", ']"')
    return command


def replace_case_insensitive(line, what, to):
    return re.compile(re.escape(what), re.IGNORECASE).sub(to, line)


def generate_clearing_commands(matching_line_keystroke_pairs):
    return [
        generate_clearing_command(line, keystroke)
        for line, keystroke in matching_line_keystroke_pairs
    ]


def execute_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, universal_newlines=True)
    if result.returncode != 0:
        messege = "{} enexpectedly failed. \n" \
                  "exitcode: {} \n" \
                  "stdout: {} \n" \
                  "stderr: {}".format(command, result.returncode, result.stdout, result.stderr)
        raise RuntimeError(messege)


def execute_commands(commands):
    for command in commands:
        execute_command(command)


if __name__ == '__main__':
    main()
