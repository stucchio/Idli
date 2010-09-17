#!/usr/bin/python

import urllib2
import json
import datetime

import bugger
github_base_api_url = "http://github.com/api/v2/json/"
dateformat = "%Y/%m/%d %H:%M:%S"

def catch_url_error(func):
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except urllib2.URLError, e:
            raise bugger.BuggerException("Could not connect to github. Error: " + str(e))
    return wrapped_func


class GithubBackend(bugger.Backend):
    def __init__(self, user, repo):
        self.__user = user
        self.__repo = repo
        self.__validate()

    @catch_url_error
    def issue_list(self, state=True):
        url = github_base_api_url + "issues/list/" + self.__user + "/" + self.__repo + "/" + self.__state_to_gh_state(state)
        json_result = urllib2.urlopen(url).read()
        issue_as_json = json.loads(json_result)
        result = []
        for i in issue_as_json["issues"]:
            date = self.__parse_date(i["created_at"])
            result.append(bugger.Issue(i["title"], i["body"], i["number"], i["user"], num_comments = i["comments"], status = i["state"], date=date))
        return result

    @catch_url_error
    def get_issue(self, issue_id):
        issue_url = github_base_api_url + "issues/show/" + self.__user + "/" + self.__repo + "/" + issue_id
        comment_url = github_base_api_url + "issues/comments/" + self.__user + "/" + self.__repo + "/" + issue_id
        try:
            issue_as_json = json.loads(urllib2.urlopen(issue_url).read())
            comments_as_json = json.loads(urllib2.urlopen(comment_url).read())
        except urllib2.HTTPError, e:
            raise bugger.BuggerException("Could not find issue with id '" + issue_id + "'")

        js_issue = issue_as_json["issue"]
        date = self.__parse_date(js_issue["created_at"])
        issue = bugger.Issue(js_issue["title"], js_issue["body"], js_issue["number"], js_issue["user"], js_issue["state"], js_issue["comments"], date)

        comments_list = comments_as_json["comments"]
        comment_result = []
        for c in comments_list:
            comment_result.append(bugger.IssueComment(issue, c["user"], "", c["body"], self.__parse_date(c["created_at"])))
        return (issue, comment_result)

    #Github queries
    def __validate(self):
        self.__validate_user()
        self.__validate_repo()

    @catch_url_error
    def __validate_user(self):
        test_url =github_base_api_url + "user/show/" + self.__user
        try:
            result = json.loads(urllib2.urlopen(test_url).read())
            return result["user"]
        except urllib2.HTTPError, e:
            raise bugger.BuggerException("Can not find user " + self.__user + " on github.")

    @catch_url_error
    def __validate_repo(self):
        test_url =github_base_api_url + "repos/show/" + self.__user + "/" + self.__repo
        try:
            result = json.loads(urllib2.urlopen(test_url).read())
            return result["repository"]
        except urllib2.HTTPError, e:
            raise bugger.BuggerException("Can not find repository " + self.__repo + " on github.")

    #Utilities
    def __state_to_gh_state(self, state):
        if (state):
            return "open"
        else:
            return "closed"

    def __parse_date(self, datestr):
        return datetime.datetime.strptime(datestr[0:19], dateformat)


