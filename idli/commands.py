import idli
import idli.backends.github as gh
import argparse

backend_list = { "github" : gh.GithubBackend,
                 }

def print_issue(issue, comments):
    print "ID: " + issue.hashcode
    print "Title: " + issue.title
    print "Creator: " + issue.creator
    print "Date: " + str(issue.date)
    print "Open: " + str(issue.status)
    print
    print issue.body
    print

    if len(comments) > 0:
        print "Comments:"
    for c in comments:
        print
        if (c.title != ""):
            print "    Comment: " + c.title.__class__
        print "    Author: " + c.creator
        print "    Date: " + str(c.date)
        print
        print "    " + c.body


main_parser = argparse.ArgumentParser(description="Command line bug reporting tool")
main_parser.add_argument('--user', dest='user', default=None, help='Username')
main_parser.add_argument('--db', dest='bugdb', default=None, help='Bug database. For example, github://project-name/')

command_parsers = main_parser.add_subparsers(title = "Commands", dest="command", help="Command to run.")

class Command(object):
    parser = None
    name = None
    def __init__(self, backend, args):
        self.backend = backend
        self.args = args

__date_format = "<%Y/%m/%d %H:%M>"

list_parser = command_parsers.add_parser("list", help="Print a list of issues")
list_parser.add_argument('--state', dest='state', type=str, default="open", choices = ["open", "closed"], help='State of issues to list (open or closed)')
list_parser.add_argument('--limit', dest='limit', type=int, default=None, help = "Number of issues to list")

class ListCommand(Command):
    name = "List issues"
    parser = list_parser
    date_format = "<%Y/%m/%d %H:%M>"

    def run(self):
        limit = self.args.limit
        self.print_issue_list(self.__state(), limit)

    def __format_issue_line(self, id, date, title, creator, num_comments):
        if date.__class__ == str:
            date_str = date
        else:
            date_str = date.strftime(self.date_format)
        return id.rjust(4) + ":" + date_str.ljust(16) + "  " + title.ljust(25) + "  " + creator.ljust(25) + "  " + str(num_comments).ljust(5)

    def __state(self):
        if (self.args.state == "open"):
            return True
        if (self.args.state == "closed"):
            return False

    def print_issue_list(self, state=True, limit=None):
        """Print list of issues to stdout."""
        issues = self.backend.issue_list(state)
        print self.__format_issue_line("ID", "date", "title", "creator", "# comments")
        if (limit is None):
            limit = len(issues)
        for i in issues[0:limit]:
            print self.__format_issue_line(i.hashcode, i.date, i.title, i.creator, i.num_comments)

view_issue_parser = command_parsers.add_parser("show", help="Display an issue")
view_issue_parser.add_argument('id', type=str, help='issue ID')

class ViewIssue(Command):
    name = "List issues"
    parser = view_issue_parser

    def run(self):
        issue, comments = self.backend.get_issue(self.args.id)
        print_issue(issue, comments)


add_issue_parser = command_parsers.add_parser("add", help="Display an issue")
add_issue_parser.add_argument('--title', type=str, default = None, help='Title of issue.')
add_issue_parser.add_argument('--body', type=str, default = None, help='Body of issue.')

class AddIssue(Command):
    name = "Add an Issue"
    parser = add_issue_parser

    def run(self):
        issue = self.backend.add_issue(self.args.title, self.args.body)
        print_issue(issue, [])

commands = { "list" : ListCommand,
             "show" : ViewIssue,
             "add" : AddIssue,
             }

def run_command(backend):
    parsed = main_parser.parse_args()
    cmd_arg = parsed.command
    command = commands[cmd_arg]
    command_runner = command(backend, parsed)
    try:
        result = command_runner.run()
    except idli.IdliException, e:
        print e.value
