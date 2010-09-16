#!/usr/bin/python

class Issue(object):
    def __init__(self, title, description, hashcode, creator, status = True, num_comments = None, date=None):
        self.title = title
        self.description = description
        self.hashcode = str(hashcode)
        self.creator = creator
        self.num_comments = int(num_comments or 0)
        self.status = status
        self.date = date

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
        pass

    def issue_list(self):
        pass

    def display_issue(self):
        pass

