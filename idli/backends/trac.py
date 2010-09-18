#!/usr/bin/python

import datetime
import argparse
import xmlrpclib

import idli
from idli.commands import configure_subparser, init_subparser
import idli.config as cfg

trac_suffix_url = "/login/xmlrpc"

CONFIG_SECTION = "Trac"

#We must add parser options for each of init_names
trac_parser = configure_subparser.add_parser("trac", help="Configure trac backend.")
trac_parser.add_argument("user", help="Trac username")
trac_parser.add_argument("password", help="Trac login password.")
#We must add parser options for each of config_names
trac_init_parser = init_subparser.add_parser("trac", help="Configure trac backend.")
trac_init_parser.add_argument("path", help="Name of repository")
trac_init_parser.add_argument("server", help="URL of trac server.")

class TracBackend(idli.Backend):
    name = CONFIG_SECTION
    init_names = ["path", "server"]
    config_names = ["user", "password"]

    def __init__(self, args):
        self.args = args
        self.__connection = None

    ##Minor utilities
    def connection(self):
        if (self.__connection is None):
            self.__connection = xmlrpclib.ServerProxy(__trac_xml_url(self.user(), self.password(), self.server(), self.path()))
        return self.__connection

    def path(self):
        return cfg.get_config_value(CONFIG_SECTION, "path")

    def server(self):
        return cfg.get_config_value(CONFIG_SECTION, "server")

    def user(self):
        return cfg.get_config_value(CONFIG_SECTION, "user")

    def password(self):
        return cfg.get_config_value(CONFIG_SECTION, "password")

    def __trac_xml_url(user, password, path, server):
        return "http://"+user+":"+password+"@"+server+"/"+path+trac_suffix_url

