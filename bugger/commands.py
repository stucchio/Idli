import bugger
import bugger.github as gh
import argparse

backend_list = { "github" : gh.GithubBackend,
                 }

main_parser = argparse.ArgumentParser(description="Command line bug reporting tool")
main_parser.add_argument('--user', dest='user', default=None, help='Username')
main_parser.add_argument('--db', dest='bugdb', default=None, help='Bug database. For example, github://project-name/')

command_parsers = main_parser.add_subparsers(help="Command to run.")

class Command(object):
    parser = None
    name = None
    def __init__(self, backend):
        self.__init_parser(self)
        self.__backend = backend

    def __init_parser(self):
        pass

class ListCommand(Command):
    name = "List issues"
    parser = command_parsers.add_parser("list", help="Print a list of issues")

    def __init_parser(self):
        parser = argparse.ArgumentParser(parents=[main_parser])
        parser.add_argument('--state', dest='state', type=str, default="open", choices = ["open", "closed"], help='State of issues to list (open or closed)')

    def __format_issue_line(id, date, title, creator, num_comments):
        if date.__class__ == str:
            date_str = date
        else:
            date_str = date.strftime("%Y/%m/%d %H:%M")
        return id.rjust(4) + ":" + date_str.ljust(16) + "  " + title.ljust(25) + "  " + creator.ljust(25) + "  " + str(num_comments).ljust(5)

    def print_issue_list(backend, state=True, limit=-1):
        """Print a list of issues to standard output."""
        issues = backend.issue_list(state)
        if state:
            print "Open issues:"
        else:
            print "Closed issues:"
        print __format_issue_line("ID", "date", "title", "creator", "# comments")
        for i in issues[0:limit]:
            print __format_issue_line(i.hashcode, i.date, i.title, i.creator, i.num_comments)
