#!/usr/bin/env python
# coding:utf-8

"Connectors for ALM (Application Lifecycle Management)"

__author__ = "Mariano Reingart (reingart@gmail.com)"
__copyright__ = "Copyright (C) 2014 Mariano Reingart"
__license__ = "GPL 3.0"

# import SDKs

try:
    # using https://github.com/michaelliao/githubpy/blob/master/github.py
    import github
except ImportError:
    github = None


TAG_MAP = {
    'type': ("bug", "enhancement", "question"),
    'resulution': ("duplicate", "wontfix", "help wanted", "invalid")
    }

 
class GitHub(object):
    "ide2py extension for integrated GitHub support"
    
    def __init__(self, username="", password="", organization="", project=""):
        
        self.gh = github.GitHub(username=username, password=password)
        self.repo = self.gh.repos(organization)(project)

    def list_tasks(self, status="open"):
        "Get a list of tasks availables in the project"
        # query github for a list of open tasks
        for issue in self.repo.issues.get(state=status, sort='created'):
            yield self.parse_task(issue)

    def parse_task(self, issue):
        "Convert a GitHub issue to a Task"
        # classify labels (ticket type and resolution)
        tags = dict([(key, label['name']) for label in issue['labels'] 
                      for key, values in TAG_MAP.items()
                      if label['name'] in values])
        # normalize the ticket data
        data = {
                'id': issue['id'],
                 'title': issue['title'],
                 'name': "Issue %s" % issue['number'],
                 'description': issue['body'],
                 'status': issue['state'],
                 'type': tags.get('type'),
                 'resolution': tags.get('resolution'),
                 'owner': issue['user']['login'],
                 'started': issue['created_at'],
                 'completed': issue['closed_at'],
                 'milestone': issue['milestone']['title'] 
                               if issue['milestone'] else '',
        }
        return data

    def create_task(self, data):
        "Create a new a task"
        issue = self.repo.issues.post(title=data['title'],
                                      body=data['description'])
        return self.parse_task(issue)


if __name__ == "__main__":
    import ConfigParser
    import pprint
    
    config = ConfigParser.ConfigParser()
    config.read('ide2py.ini')
    
    kwargs = dict(config.items("GITHUB"))
    kwargs['organization'] = 'reingart'
    kwargs['project'] = 'prueba'
    print kwargs
    gh = GitHub(**kwargs)
    pprint.pprint(list(gh.list_tasks(status="open")))
    task = gh.create_task({'title': 'prueba', 'description': '1234...'})
    pprint.pprint(task)

