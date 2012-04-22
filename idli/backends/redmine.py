#!/usr/bin/python

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

class RedmineBackend(idli.Backend):
    name = "redmine"
    config_section = "Redmine"
    init_names = [ ("base_url", "Base URL to access"),
                   ("api_token", "Redmine API token"),
                   ("project_id", "Project ID"),
                   ("Username", "Real name, as given in redmine. E.g., Chris Stucchio"),
                   ]
    config_names = [  ]

    def __init__(self, args, base_url=None, token=None, project_id=None):
        self.args = args
        self.__base_url = base_url
        self.__token = token
        self.__project_id = project_id

        try: #If we are properly configured, try to get statuses
            self.token()
            self.__get_statuses()
        except idli.config.IdliMissingConfigException:
            pass

    def base_url(self):
        return self.__base_url or self.get_config("base_url")

    def token(self):
        return self.__token or self.get_config("api_token")

    def project_id(self):
        return self.__project_id or self.get_config("project_id")

    def issue_list(self, state=True):
        params = { 'project_id' : self.project_id(), 'limit' : 100,  'status_id' : state}
        issues = []
        result = json.loads(self.__url_request("/issues.json", params = params) )
        total_results = result['total_count']
        json_results = result['issues']
        while (len(json_results) < total_results):
            params = { 'project_id' : self.project_id(), 'limit' : 100, 'offset' : len(json_results), 'status_id' : state }
            result = json.loads(self.__url_request("/issues.json", params = params) )
            json_results += result['issues']
            total_results = result['total_count']

        return [self.__parse_issue(i) for i in json_results]

    def filtered_issue_list(self, state=True, mine=False, tag=None):
        issues = self.issue_list(state)
        if mine:
            issues = [i for i in issues if i.owner == self.username()]
        if tag:
            issues = [i for i in issues if tag in i.tags]
        return issues

    DATE_FORMAT = '%Y/%m/%d %H:%M:%S'
    def __parse_date(self, d):
        tz_delta = datetime.timedelta(hours=int(d[-6:])/100)
        return datetime.datetime.strptime(d[0:19], self.DATE_FORMAT) + tz_delta

    def __parse_issue(self, i):
        issue = idli.Issue(i['subject'], i['description'], i['id'], i['author']['name'], status=i['status']['name'], create_time=self.__parse_date(i['created_on']))
        if i.has_key('assigned_to'):
            issue.owner = i['assigned_to']['name']
        return issue

    def __url_request(self, suffix, params={}):
        headers = { 'Content-Type' : 'application/json' }
        auth = (self.token(), "null")
        response = requests.get(self.base_url() + suffix, auth=auth, params=params, headers=headers)
        if (response.status_code - (response.status_code % 100)) != 200: #200 responses are all legitimate
            raise HttpRequestException("HTTP error", response.status_code)
        return response.content

    def __get_statuses(self):
        try:
            result = json.loads(self.__url_request("/issue_statuses.json"))
            idli.set_status_mapping(d)
        except HttpRequestException, e:
            idli.set_status_mapping({ 'New' : True, 'Closed' : False, 'In Progress' : True, 'Rejected' : False, 'Resolved' : False, 'Feedback' : True })
