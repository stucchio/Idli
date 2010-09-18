from ConfigParser import ConfigParser, NoSectionError
import os
import argparse
import idli

IDLI_PROJECT_FILENAME = ".idli"

class IdliMissingConfigException(idli.IdliException):
    def __init__(self, section, key):
        self.value = (section, key)
    def __str__(self):
        return repr(self.value)

def global_config_filename():
    return os.path.join(os.getenv("HOME"), ".idli_config")

def local_config_filename():
    pwd = os.getenv("PWD")
    cfg_filename = os.path.join(pwd, IDLI_PROJECT_FILENAME)
    while (not os.path.exists(cfg_filename)) and (pwd != "/"):
        pwd = os.path.split(pwd)[0]
        cfg_filename = os.path.join(pwd, IDLI_PROJECT_FILENAME)
    if (pwd == "/"):
        return os.path.join(os.getenv("PWD"), IDLI_PROJECT_FILENAME)
    else:
        return os.path.join(pwd, IDLI_PROJECT_FILENAME)

def global_config_file():
    open(global_config_filename(),'w').close() # Equivalent to touching the file, make sure it exists first
    return open(global_config_filename(),'r+w')

global_cfg = ConfigParser()
local_cfg = ConfigParser()

def get_config_value(section, name):
    if (local_cfg.has_option(section, name)): #Local should override global
        return local_cfg.get(section, name)
    if (global_cfg.has_option(section, name)):
        return global_cfg.get(section, name)
    raise IdliMissingConfigException(section, name)

class StoreConfigurationAction(argparse.Action):
    def __config(self, global_config):
        if (global_config):
            return global_cfg
        else:
            return local_cfg

    def __write(self, global_config):
        if (global_config):
            self.__config(global_config).write(open(global_config_filename(), 'w'))
        else:
            self.__config(global_config).write(open(local_config_filename(), 'w'))

    def __call__(self, parser, namespace, value, option_string=None, global_config=True):
        cfg = self.__config(global_config)
        if (not cfg.has_section(self.section)):
            cfg.add_section(self.section)
        cfg.set(self.section, self.name, value)
        self.__write(global_config)

def add_store_configuration_parser(parser, section_name, value_name, help, optional = True):
    """A command line actoin to store global configuration options."""
    class StoreAction(StoreConfigurationAction):
        section = section_name
        name = value_name
    if (optional):
        parser.add_argument("--" + value_name, dest=value_name, action = StoreAction, help = help)
    else:
        parser.add_argument(value_name, action = StoreAction, help = help)

#Try to load configuration files. This need not succeed.
try:
    global_cfg.readfp(open(global_config_filename(), "r+w"))
except IOError, e:
    pass # If config files don't exist, don't worry about it yet
try:
    local_cfg.readfp(open(local_config_filename(), 'r+w'))
except IOError, e:
    pass # If config files don't exist, don't worry about it yet

if __name__=="__main__":
    pass

