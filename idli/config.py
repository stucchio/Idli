from ConfigParser import ConfigParser, NoSectionError
import os
import argparse
import idli

class IdliMissingConfigException(idli.IdliException):
    def __init__(self, section, key):
        self.value = (section, key)
    def __str__(self):
        return repr(self.value)

def global_config_filename():
    return os.path.join(os.getenv("HOME"), ".idli_config")

def global_config_file():
    open(global_config_filename(),'w').close() # Equivalent to touching the file, make sure it exists first
    return open(global_config_filename(),'r+w')

global_cfg = ConfigParser()
global_cfg.readfp(global_config_file())

def get_config_value(section, name):
    try:
        return global_cfg.get(section, name)
    except NoSectionError, e:
        raise IdliMissingConfigException(section, name)

class StoreConfigurationAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if (not global_cfg.has_section(self.section)):
            global_cfg.add_section(self.section)
        global_cfg.set(self.section, self.name, value)
        global_cfg.write(config_file())

def add_store_configuration_parser(parser, section_name, value_name, help, optional = True):
    """A command line actoin to store global configuration options."""
    class StoreAction(StoreConfigurationAction):
        section = section_name
        name = value_name
    if (optional):
        parser.add_argument("--" + value_name, dest=value_name, action = StoreAction, help = help)
    else:
        parser.add_argument(value_name, action = StoreAction, help = help)

if __name__=="__main__":
    pass

