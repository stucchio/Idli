from ConfigParser import ConfigParser, NoSectionError
import os
import argparse

def config_filename():
    return os.path.join(os.getenv("HOME"), ".idli_config")

def config_file():
    open(config_filename(),'w').close() # Equivalent to touching the file, make sure it exists first
    return open(config_filename(),'r+w')

configuration = ConfigParser()
configuration.readfp(config_file())

def get_config_value(section, name):
    try:
        return configuration.get(section, name)
    except NoSectionError, e:
        return None

class StoreConfigurationAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if (not configuration.has_section(self.section)):
            configuration.add_section(self.section)
        configuration.set(self.section, self.name, value)
        configuration.write(config_file())

def add_store_configuration_parser(parser, section_name, value_name, help):
    class StoreAction(StoreConfigurationAction):
        section = section_name
        name = value_name
    parser.add_argument("--" + value_name, dest=value_name, action = StoreAction, help = help)

if __name__=="__main__":
    pass

