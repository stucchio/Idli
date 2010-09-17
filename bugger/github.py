#!/usr/bin/python

from urllib2 import urlopen
import json
import datetime

import bugger
github_base_api_url = "http://github.com/api/v2/json/"
dateformat = "%Y/%m/%d %H:%M:%S"

class GithubBackend(bugger.Backend):

    def __init__(self, user, repo):
        self.__user = user
        self.__repo = repo

    def issue_list(self, state=True):
        url = github_base_api_url + "issues/list/" + self.__user + "/" + self.__repo + "/"
        if (state):
            url += "open"
        else:
            url += "closed"
        json_result = urlopen(url).read()
        issue_as_json = json.loads(json_result)
        result = []
        for i in issue_as_json["issues"]:
            date = self.__parse_date(i["created_at"])
            result.append(bugger.Issue(i["title"], i["body"], i["number"], i["user"], num_comments = i["comments"], status = i["state"], date=date))
        return result

    def __parse_date(self, datestr):
        return datetime.datetime.strptime(datestr[0:19], dateformat)

    def get_issue(self, issue_id):
        issue_url = github_base_api_url + "issues/show/" + self.__user + "/" + self.__repo + "/" + issue_id
        comment_url = github_base_api_url + "issues/comments/" + self.__user + "/" + self.__repo + "/" + issue_id
        issue_as_json = json.loads(urlopen(issue_url).read())
        js_issue = issue_as_json["issue"]
        date = self.__parse_date(js_issue["created_at"])
        issue = bugger.Issue(js_issue["title"], js_issue["body"], js_issue["number"], js_issue["user"], js_issue["state"], js_issue["comments"], date)

        comments_as_json = json.loads(urlopen(comment_url).read())
        comments_list = comments_as_json["comments"]
        comment_result = []
        for c in comments_list:
            comment_result.append(bugger.IssueComment(issue, c["user"], "", c["body"], self.__parse_date(c["created_at"])))
        return (issue, comment_result)



