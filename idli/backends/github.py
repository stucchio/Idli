#!/usr/bin/python

import urllib
import urllib2
import json
import datetime
import requests

import idli
import idli.config as cfg

github_base_api_url = "http://github.com/api/v2/json/"
dateformat = "%Y/%m/%d %H:%M:%S"

class HttpRequestException(Exception):
    def __init__(self, value, status_code):
        super(HttpRequestException, self).__init__(value)
        self.value = value
        self.status_code = status_code

    def __unicode__(self):
        return "HttpError: " + unicode(self.status_code) + ", " + unicode(self.value)

def catch_url_error(func):
    def wrapped_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HttpRequestException, e:
            raise idli.IdliException("Could not connect to github. Error: " + unicode(e))
    return wrapped_func

def catch_HTTPError(func):
    def wrapped_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except HttpRequestException, e:
            if (e.status_code == 401):
                raise idli.IdliException("Authentication failed.\n\nCheck your idli configuration. The most likely cause is incorrect values for 'user' or 'password' variables in the [Github] section of the configuration files:\n    " + cfg.local_config_filename() + "\n    " + cfg.global_config_filename() + ".\n\nMake sure you check both files - the values in " + cfg.local_config_filename() + " will override the values in " + cfg.global_config_filename() + "." + "\n\n" + str(e))
            if (e.status_code == 404):
                self.validate()
            raise e
    return wrapped_func

def catch_missing_config(func):
    def wrapped_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except cfg.IdliMissingConfigException, e:
            raise idli.IdliException("You must configure idli for github first. Run 'idli configure github' for options.")
    return wrapped_func

CONFIG_SECTION = "Github"

class GithubBackend(idli.Backend):
    name = "github"
    config_section = "Github"
    init_names = [ ("repo", "Name of repository"),
                   ("owner", "Owner of repository (github username).")
                   ]
    config_names = [ ("user", "Github username"),
                     ("password", "Github password"),
                     ]

    def __init__(self, args, repo=None, auth = None):
        self.args = args
        if (repo is None):
            self.__repo_owner, self.__repo = None, None
        else:
            self.repo_owner, self.repo_name = repo
        if (auth is None):
            self.__user, self.__password = None, None
        else:
            self.__user, self.__password = auth

    def repo(self):
        return self.__repo or self.get_config("repo")

    def repo_owner(self):
        return self.__repo_owner or self.get_config("owner")

    def username(self):
        return self.__user or self.get_config("user")

    def password(self):
        return self.__password or self.get_config("password")

    def auth(self):
        if self.username() and self.password():
            return (self.username(), self.password())
        return None

    @catch_missing_config
    @catch_url_error
    @catch_HTTPError
    def add_issue(self, title, body, tags=[]):
        url = github_base_api_url + "issues/open/" + self.repo_owner() + "/" + self.repo()
        result = self.__url_request(url, title=title, body=body)
        issue = self.__parse_issue(json.loads(result)["issue"])
        if tags:
            self.tag_issue(issue.id, tags)
            issue = self.get_issue(issue.id)
        return (issue, [])

    @catch_missing_config
    @catch_url_error
    @catch_HTTPError
    def tag_issue(self, issue_id, tags, remove_tags=False):
        for t in tags:
            url = self.__add_label_url(issue_id, t, remove_tags)
            result = json.loads(self.__url_request(url))
            if (not (t in result['labels'])) and (not remove_tags):
                raise idli.IdliException("Failed to add tag to issue " + str(issue_id) + ". The issue list may be in an inconsistent state.")
        return self.get_issue(issue_id)

    @catch_url_error
    @catch_HTTPError
    def issue_list(self, state=True):
        url = github_base_api_url + "issues/list/" + self.repo_owner() + "/" + self.repo() + "/" + self.__state_to_gh_state(state)
        result = self.__url_request(url)
        issue_as_json = json.loads(result)
        result = []
        for i in issue_as_json["issues"]:
            result.append(self.__parse_issue(i))
        return result

    @catch_url_error
    def get_issue(self, issue_id, get_comments=True):
        issue_url = github_base_api_url + "issues/show/" + self.repo_owner() + "/" + self.repo() + "/" + issue_id
        comment_url = github_base_api_url + "issues/comments/" + self.repo_owner() + "/" + self.repo() + "/" + issue_id
        try:
            issue_as_json = json.loads(self.__url_request(issue_url))
            comments_as_json = json.loads(self.__url_request(comment_url))
        except urllib2.HTTPError, e:
            self.validate()
            raise idli.IdliException("Could not find issue with id '" + issue_id + "'")

        js_issue = issue_as_json["issue"]
        date = self.__parse_date(js_issue["created_at"])
        issue = self.__parse_issue(issue_as_json["issue"])
        comments_list = comments_as_json["comments"]
        comment_result = []
        for c in comments_list:
            comment_result.append(self.__parse_comment(issue, c))
        return (issue, comment_result)

    @catch_missing_config
    @catch_HTTPError
    @catch_url_error
    def add_comment(self, issue_id, body):
        url = github_base_api_url + "issues/comment/" + self.repo_owner() + "/" + self.repo() + "/" + str(issue_id)
        result_str = self.__url_request(url, comment=body)
        comment = self.__parse_comment(None, json.loads(result_str)['comment'])
        return comment

    @catch_missing_config
    @catch_url_error
    @catch_HTTPError
    def resolve_issue(self, issue_id, status = "closed", message = None):
        self.add_comment(issue_id, message)
        status_url = self.__resolution_code_to_url[status]
        url = github_base_api_url + "issues/" + status_url + "/" + self.repo_owner() + "/" + self.repo() + "/" + str(issue_id)
        issue = self.__parse_issue(json.loads(self.__url_request(url))["issue"])
        return issue
    __resolution_code_to_url = { "closed" : "close", "open" : "reopen" }

    #Github queries
    def validate(self):
        self.__validate_user()
        self.__validate_repo()

    @catch_url_error
    def __validate_user(self):
        test_url = github_base_api_url + "user/show/" + self.repo_owner()
        try:
            result = json.loads(urllib2.urlopen(test_url).read())
            return result["user"]
        except urllib2.HTTPError, e:
            raise idli.IdliException("Can not find user " + self.repo_owner() + " on github.")

    @catch_url_error
    def __validate_repo(self):
        test_url = github_base_api_url + "repos/show/" + self.repo_owner() + "/" + self.repo()
        try:
            result = json.loads(urllib2.urlopen(test_url).read())
            return result["repository"]
        except urllib2.HTTPError, e:
            raise idli.IdliException("Can not find repository " + self.repo() + " on github.")

    #Utilities
    def __url_request(self, url, **kwargs):
        response = requests.get(url, auth=self.auth(), params=kwargs)
        if (response.status_code - (response.status_code % 100)) != 200: #200 responses are all legitimate
            raise HttpRequestException("HTTP error", response.status_code)
        return response.content

    def __parse_comment(self, issue, cdict):
        return idli.IssueComment(issue, cdict["user"], "", cdict["body"], self.__parse_date(cdict["created_at"]))

    def __parse_issue(self, issue_dict):
        create_time = self.__parse_date(issue_dict["created_at"])
        return idli.Issue(issue_dict["title"], issue_dict["body"],
                            issue_dict["number"], issue_dict["user"],
                            num_comments = issue_dict["comments"], status = issue_dict["state"],
                            create_time=create_time, tags=issue_dict["labels"])

    def __state_to_gh_state(self, state):
        if (state):
            return "open"
        else:
            return "closed"

    def __add_label_url(self, issue_id, tag, remove=False):
        url = github_base_api_url + "issues/label"
        if (remove):
            url += "/remove"
        else:
            url += "/add"
        url += "/" + self.repo_owner() + "/" + self.repo() + "/" + tag + "/" + str(issue_id)
        return url

    def __parse_date(self, datestr):
        return datetime.datetime.strptime(datestr[0:19], dateformat)


