# This file is part of azulejo
#
# Author: Pedro and Gilles
#
# This code takes care of setting up or loading configurations and shortcuts.
# The configurations are saved as json files. There is one config file, which contains the path
# to the currently selected shortcut file.
# The shortcut files contain the shortcuts which can be used.

import json
import os.path
from collections import deque

conf_filename = "~/.azulejo/config.js"
filenames = {conf_filename: "initial_config.json", \
             "~/.azulejo/Shortcuts/numpad.js": "initial_shortcuts_numpad.json", \
             "~/.azulejo/Shortcuts/no_numpad.js": "initial_shortcuts_no_numpad.json"}
expanded_filenames = {}
shortcut_filenames = deque()


def read_file(path):
    '''
    Returns file content as string.
    @type path: str
    @rtype: str
    @return: file as string
    '''
    """Returns file content as string."""
    file_handler = open(path, 'r')
    content = file_handler.read()
    file_handler.close()
    return content


def get_initial_content(filename):
    '''
    Returns the initial values as string.
    @param filename: a key used in the C{filenames}
    @type filename: str
    @rtype: str
    @return: content of the initial file
    '''
    this_dir = os.path.dirname(os.path.abspath(__file__))
    #get the name of the appropriate initial file, then get the path of that file
    initial_config_path = os.path.join(this_dir, filenames[filename])
    return read_file(initial_config_path)


def create_initial_file(filename):
    '''
    Creates the file with its content for the given C{filename}
    @param filename: a key used in the C{filenames}
    @type filename: String
    '''
    #check if the path to the directory exists
    conf_dir = os.path.dirname(expanded_filenames[filename])
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)

    #Create a file with config values.
    fw = open(expanded_filenames[filename], 'w')
    raw_json = get_initial_content(filename)
    fw.write(raw_json)
    fw.close()


def check_initial_files():
    '''
    Checks if the files from the C{filenames}-dict exist, if not they will be created.
    '''
    for filename in filenames.iterkeys():
        expanded_filename = os.path.expanduser(filename)
        expanded_filenames[filename] = expanded_filename
        if not os.path.isfile(expanded_filename):
            print "Starting azulejo by creating file: '%s'" % (expanded_filename)
            create_initial_file(filename)


def get_config_data():
    '''
    Reads the config file as json and gets the path of the shortcut file from it.
    That shortcut file is then parsed. The parsed content is then returned as a list,
    which contains dicts with information about the actions.
    @rtype: list
    @return: A list of dicts, containing information about an action
    '''
    expanded_conf_filename = expanded_filenames[conf_filename]
    json_string = read_file(os.path.expanduser(expanded_conf_filename))

    interpreted_json = json.loads(json_string)
    shortcut_data = interpreted_json[0]
    conf_data = interpreted_json[1:]

    shortcut_filename = os.path.expanduser(shortcut_data["shortcut_file_to_load"])
    json_string = read_file(shortcut_filename)
    conf_data += json.loads(json_string)

    return conf_data


def get_config_data_first_time():
    '''
    Checks if the initial config files already exist, if not then they are created.
    Then checks which config files exists, as the user might have added a file himself.
    The path to these files is saved in the global deque C{shortcut_filenames}.
    Finally reads and returns config data via C{get_config_data}.
    @rtype: list
    @return: Returns config data
    '''
    # TODO remove global variable. Thus configuration needs to be a class.
    global shortcut_filenames
    check_initial_files()
    shortcut_filenames = deque(os.listdir(os.path.expanduser("~/.azulejo/Shortcuts")))
    for i in range(len(shortcut_filenames)):
        shortcut_filenames[i] = "~/.azulejo/Shortcuts/" + shortcut_filenames[i]
    return get_config_data()


def switch_shortcut_file():
    '''
    Load the next shortcut file and return its name as string
    @rtype: str
    @return: a filename key used in the C{filenames}
    '''
    # TODO remove global variable. Thus configuration needs to be a class.
    global shortcut_filenames
    expanded_conf_filename = expanded_filenames[conf_filename]
    json_string = read_file(os.path.expanduser(expanded_conf_filename))

    interpreted_json = json.loads(json_string)
    shortcut_data = interpreted_json[0]

    for filename in shortcut_filenames:
        if filename != shortcut_data["shortcut_file_to_load"]:
            shortcut_data["shortcut_file_to_load"] = filename
            break

    shortcut_filenames.rotate()

    print "Switched to Shortcut file: '%s'" % (shortcut_data["shortcut_file_to_load"])
    conf_file = open(expanded_conf_filename, "w")
    conf_file.writelines(json.dumps([shortcut_data], sort_keys=True, indent=4))
    conf_file.close()

    return shortcut_data["shortcut_file_to_load"]
