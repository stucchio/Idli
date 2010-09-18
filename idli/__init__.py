#!/usr/bin/python

class Issue(object):
    def __init__(self, title, body, hashcode, creator, status = True, num_comments = None, date=None):
        self.title = title
        self.body = body
        self.hashcode = str(hashcode)
        self.creator = creator
        self.num_comments = int(num_comments or 0)
        self.status = self.__parse_status(status)
        self.date = date

    def __parse_status(self, status):
        if (status.__class__ == bool):
            return status
        if (status.__class__ == str or status.__class__ == unicode):
            return self.__status_mapping[status.lower()]

    __status_mapping = {"open" : True,
                        "closed" : False,
                        "true" : True,
                        "false" : False
                        }
    def __str__(self):
        return "Issue(" + self.hashcode + ", " + self.title + ", " + self.creator + ", " + str(self.status) + ")"

class IssueComment(object):
    def __init__(self, issue, creator, title, body, date=None):
        self.issue = issue
        self.creator = creator
        self.title = title
        self.body = body
        self.date = date

class Backend(object):
    def __init__(self):
        raise IdliException("That functionality is not implemented by this backend.")

    def initialize(self):
        print "Initializing " + self.name + " project."
        import idli.config as cfg
        cfg.set_config_value("project", "type", self.name, global_val=False)

    def configure(self, args):
        raise IdliException("That functionality is not implemented by this backend.")

    def add_issue(self, title, body):
        raise IdliException("That functionality is not implemented by this backend.")

    def issue_list(self):
        raise IdliException("That functionality is not implemented by this backend.")

    def get_issue(self, issue_id):
        raise IdliException("That functionality is not implemented by this backend.")

class IdliException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
