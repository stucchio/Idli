#!/usr/bin/python

from datetime import datetime
import argparse
import xmlrpclib
import socket

import idli
from idli.commands import configure_subparser, init_subparser
import idli.config as cfg

trac_suffix_url = "/login/xmlrpc"

CONFIG_SECTION = "Trac"

def catch_socket_errors(func):
    def __wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.gaierror, e:
            raise idli.IdliException("Error connecting to trac server " + trac_server_url() + ".\nCheck your config file and make sure the path is correct: " + cfg.local_config_filename() + ".\n\n" + str(e))
    return __wrapped


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

    @catch_socket_errors
    def issue_list(self, state=True):
        ticket_id_list = []
        if (state):
            ticket_id_list = self.connection().ticket.query("status!=closed")
        else:
            ticket_id_list = self.connection().ticket.query("status=closed")
        multicall = xmlrpclib.MultiCall(self.connection()) # We try to get actual tickets in one http request
        for ticket in ticket_id_list:
            multicall.ticket.get(ticket)
        return [self.__convert_issue(t) for t in multicall()]

    ##Minor utilities
    def connection(self):
        if (self.__connection is None):
            self.__connection = xmlrpclib.ServerProxy(trac_xml_url())
        return self.__connection

    def path(self):
        return cfg.get_config_value(CONFIG_SECTION, "path")

    def server(self):
        return cfg.get_config_value(CONFIG_SECTION, "server")

    def user(self):
        return cfg.get_config_value(CONFIG_SECTION, "user")

    def password(self):
        return cfg.get_config_value(CONFIG_SECTION, "password")

    def __convert_issue(self, t):
        issue_id = t[0]
        i = t[3] # Rest of ticket as a dictionary
        owner = None
        if i['owner'] != "somebody":
            owner = i['owner']
        status = True
        if i['status'] == "closed":
            status = False
        return idli.Issue(i["summary"], i["description"], str(issue_id), i['reporter'],
                          status, num_comments = 0, create_time=self.__convert_date(t[1]),
                          last_modified = self.__convert_date(t[2]), owner=owner)

    def __convert_date(self, d):
        return datetime(*(d.timetuple()[0:6]))

    def __ticket_status(self, t):
        if t['status'] == "closed":
            return False
        return True

def trac_server_url():
    return "http://" + cfg.get_config_value(CONFIG_SECTION, "server")+"/"+cfg.get_config_value(CONFIG_SECTION, "path")

def trac_xml_url():
    return "http://"+cfg.get_config_value(CONFIG_SECTION, "user")+":"+cfg.get_config_value(CONFIG_SECTION, "password")+"@"+cfg.get_config_value(CONFIG_SECTION, "server")+"/"+cfg.get_config_value(CONFIG_SECTION, "path")+trac_suffix_url

