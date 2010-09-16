#!/usr/bin/python

from urllib2 import urlopen
import json
import datetime

import bugger

class GithubBackend(bugger.Backend):
    __github_base_api_url = "http://github.com/api/v2/json/"
    def __init__(self, user, repo):
        self.__user = user
        self.__repo = repo

    def __parse_state(self, state):
        if state == "open":
            return True
        else:
            return False

    def issue_list(self, state=True):
        url = self.__github_base_api_url + "issues/list/" + self.__user + "/" + self.__repo + "/"
        if (state):
            url += "open"
        else:
            url += "closed"
        json_result = urlopen(url).read()
        issue_as_json = json.loads(json_result)
        result = []
        for i in issue_as_json["issues"]:
            date = datetime.datetime.strptime(i["created_at"][0:19], "%Y/%m/%d %H:%M:%S")
            result.append(bugger.Issue(i["title"], i["body"], i["number"], i["user"], num_comments = i["comments"], status = self.__parse_state(i["state"]), date=date))
        return result



