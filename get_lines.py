"""
A simple module for counting the number of lines the bot uses.
The bot uses the number as its status in Discord.
"""

import os

suffixes = [".py", ".html", ".js", ".css", ".json", ".txt", ".wsgi"]


def get_lines(path):
    """
    Returns the number of lines in all files in the given path.
    """
    lines = 0
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath[-3:] in suffixes:
                with open(filepath, 'r') as f:
                    for line in f:
                        lines += 1

    return lines


def get_characters(path):
    characters = 0
    for subdir, dirs, files in os.walk(path):
        for file in files:
            filepath = subdir + os.sep + file
            if filepath[-3:] in suffixes:
                with open(filepath, 'r') as f:
                    for line in f:
                        characters += len(line)

    return characters
