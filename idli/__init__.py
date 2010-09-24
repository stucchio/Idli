#!/usr/bin/python

class Issue(object):
    def __init__(self, title, body, hashcode, creator, status = True, num_comments = None, create_time=None, last_modified=None, owner=None):
        self.title = title
        self.body = body
        self.hashcode = str(hashcode)
        self.creator = creator
        self.num_comments = int(num_comments or 0)
        self.status = self.__parse_status(status)
        self.create_time = create_time
        self.last_modified = last_modified

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
        section_name = self.config_section or self.name
        print "Initializing " + self.name + " project."
        import idli.config as cfg
        for name in self.init_names:
            cfg.set_config_value(section_name, name, self.args.__dict__[name], global_val=False)
        cfg.set_config_value("project", "type", self.name, global_val=False)
        print "Wrote configuration to " + cfg.local_config_filename()

    def configure(self):
        section_name = self.config_section or self.name
        print "Configuring backend  " + self.name
        import idli.config as cfg
        for name in self.config_names:
            cfg.set_config_value(section_name, name, self.args.__dict__[name], global_val=not self.args.local_only)
        cfg.set_config_value("project", "type", self.name, global_val=not self.args.local_only)
        if (not self.args.local_only):
            print "Wrote configuration to " + cfg.global_config_filename()
        else:
            print "Added local configuration to " + cfg.global_config_filename()

    def add_issue(self, title, body):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

    def issue_list(self, state=True):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

    def get_issue(self, issue_id):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

    def resolve_issue(self, issue_id, status = "closed", message = None):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

    def add_comment(self, issue_id, body):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

    def assign_issue(self, issue_id, user, message):
        raise IdliNotImplementedException("That functionality is not implemented by this backend.")

class IdliException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class IdliNotImplementedException(IdliException):
    pass
