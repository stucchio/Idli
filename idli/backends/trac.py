#!/usr/bin/python

from datetime import datetime
import xmlrpclib
import socket

import idli
import idli.config as cfg

trac_suffix_url = "/login/xmlrpc"

CONFIG_SECTION = "Trac"

def catch_socket_errors(func):
    def __wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except socket.gaierror, e:
            raise idli.IdliException("Error connecting to trac server " + trac_server_url() + ".\nCheck your config file and make sure the path is correct: " + cfg.local_config_filename() + ".\n\n" + unicode(e))
        except socket.error, e:
            raise idli.IdliException("Error connecting to trac server " + trac_server_url() + ".\nCheck your config file and make sure the path is correct: " + cfg.local_config_filename() + ".\n\n" + unicode(e))
        except xmlrpclib.Fault, e:
            if e.faultCode == 403:
                raise idli.IdliException("Trac's permissions are not set correctly. Run\n $ trac-admin TRACDIR permission add authenticated XML_RPC\nto enable XML_RPC permissions (which are required by idli).")
            else:
                raise idli.IdliException("Error connecting to trac server " + trac_server_url() + ".\nCheck your config file and make sure the path is correct: " + cfg.local_config_filename() + ".\n\n" + unicode(e))
        except xmlrpclib.ProtocolError, e:
            raise idli.IdliException("Protocol error. This probably means that the XmlRpc plugin for trac is not enabled. Follow the inunicodeuctions here to install it:\nhttp://trac-hacks.org/wiki/XmlRpcPlugin\n\n"+unicode(e))
    return __wrapped

class TracBackend(idli.Backend):
    config_section = CONFIG_SECTION
    name = "trac"
    init_names = [ ("server", "URL of trac server."),
                   ("path", "Name of repository")
                   ]
    config_names = [("user", "Trac username"),
                    ("password", "Trac login password.")
                    ]

    def __init__(self, args):
        self.args = args
        self.__connection = None

    @catch_socket_errors
    def issue_list(self, state=True, mine=None):
        ticket_id_list = []
        if (state):
            ticket_id_list = self.ticket_api().query("status!=closed")
        else:
            ticket_id_list = self.ticket_api().query("status=closed")
        multicall = xmlrpclib.MultiCall(self.connection()) # We try to get actual tickets in one http request
        for ticket in ticket_id_list:
            multicall.ticket.get(ticket)
        issues = [self.__convert_issue(t) for t in multicall()]
        if mine:
            issues = [i for i in issues if i.owner == self.username()]
        return issues

    @catch_socket_errors
    def add_comment(self, issue_id, body):
        self.ticket_api().update(int(issue_id), body, {})

    @catch_socket_errors
    def get_issue(self, issue_id):
        issue = self.__convert_issue(self.ticket_api().get(int(issue_id)))
        comments = [ self.__convert_comment(c, issue) for c in self.ticket_api().changeLog(int(issue_id)) if c[2] == 'comment']
        return (issue, comments)

    @catch_socket_errors
    def resolve_issue(self, issue_id, status = "closed", message = None):
        actions = self.ticket_api().getActions(issue_id)
        if ('resolve' in [a[0] for a in actions]):
            ticket = self.ticket_api().update(int(issue_id), message, { 'status' : 'fixed', 'action' : 'resolve'})
            return self.__convert_issue(ticket)
        raise idli.IdliException("Can not resolve issue " + issue_id + ". Perhaps it is already resolved?")

    @catch_socket_errors
    def add_issue(self, title, body, tags=[]):
        ticket_id = self.ticket_api().create(title, body)
        return ( self.__convert_issue(self.ticket_api().get(ticket_id)), [] )

    @catch_socket_errors
    def assign_issue(self, issue_id, user, message):
        actions = self.ticket_api().getActions(issue_id)
        if ('reassign' in [a[0] for a in actions]):
            ticket = self.ticket_api().update(int(issue_id), message, { 'owner' : user, 'status' : 'assigned'})
            return self.__convert_issue(ticket)
        raise idli.IdliException("Failed to assign ticket.")

    ##Minor utilities
    def ticket_api(self):
        return self.connection().ticket

    def connection(self):
        if (self.__connection is None):
            self.__connection = xmlrpclib.ServerProxy(trac_xml_url())
        return self.__connection

    def path(self):
        return self.get_config("path")

    def server(self):
        return self.get_config("server")

    def username(self):
        return self.get_config("user")

    def password(self):
        return self.get_config("password")

    def __convert_comment(self, c, issue):
        return idli.IssueComment(issue, unicode(c[1]), "", unicode(c[4]), date=c[0])

    def __convert_issue(self, t):
        issue_id = t[0]
        i = t[3] # Rest of ticket as a dictionary
        owner = None
        if i['owner'] != "somebody":
            owner = i['owner']
        status = True
        if i['status'] == "closed":
            status = False
        return idli.Issue(i["summary"], i["description"], unicode(issue_id), i['reporter'],
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

