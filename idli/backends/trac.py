#!/usr/bin/python

from datetime import datetime
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

    def issue_list(self, state=True):
        conn = self.connection()
        ticket_id_list = []
        if (state):
            ticket_id_list = conn.ticket.query("status!=closed")
        else:
            ticket_id_list = conn.ticket.query("status=closed")
        tickets_xmlrpc = [conn.ticket.get(n) for n in ticket_id_list]
        return [self.__convert_issue(t) for t in tickets_xmlrpc]

    ##Minor utilities
    def connection(self):
        print "Connecting to " + self.__trac_xml_url(self.user(), self.password(), self.server(), self.path())
        if (self.__connection is None):
            self.__connection = xmlrpclib.ServerProxy(self.__trac_xml_url(self.user(), self.password(), self.server(), self.path()))
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

    def __trac_xml_url(self, user, password, server, path):
        return "http://"+user+":"+password+"@"+server+"/"+path+trac_suffix_url

