import idli
import idli.util as util
import idli.config as config

import argparse

commands = {}

main_parser = argparse.ArgumentParser(description="Command line bug reporting tool")

command_parsers = main_parser.add_subparsers(title = "Commands", dest="command", help="Command to run.")

class Command(object):
    parser = None
    name = None
    flags = {}
    required = {}
    options = {}

    def __init__(self, args, backend = None):
        from idli.backends import get_backend_or_fail
        self.args = args
        self.backend = backend or get_backend_or_fail()(self.args)

__date_format = "<%Y/%m/%d %H:%M>"

class ConfigureCommand(Command):
    name = "config"
    flags = [ ("local_only", 'If this flag is set, the configuration information will be used only for this project.'),
              ]

    def __init__(self, args, backend = None):
        from idli.backends import get_backend_or_fail
        self.args = args
        self.backend = backend or get_backend_or_fail(args.backend_name)(self.args)

    def run(self):
        self.backend.configure()

def __register_command(cmd, help):
    cmd_parser = command_parsers.add_parser(cmd.name, help=help)
    for (name, help) in cmd.flags: # Configure flags.
        cmd_parser.add_argument('--' + name.replace('_','-'), dest=name, action='store_const', const=True, default=False, help=help)
    for name, args in cmd.options: # Configure options
        cmd_parser.add_argument('--'+name, dest=name, **args)

    for (name, args) in cmd.required: # Configure arguments
        cmd_parser.add_argument(dest=name, **args)
    commands[cmd.name] = cmd
    return cmd_parser

configure_parser = __register_command(ConfigureCommand, help="Configure a backend.")
configure_subparser = configure_parser.add_subparsers(dest="backend_name", help='Backend to configure')

class InitializeCommand(Command):
    parser = configure_parser
    name = "init"

    def __init__(self, args, backend = None):
        from idli.backends import get_backend_or_fail
        self.args = args
        self.backend = backend or get_backend_or_fail(args.backend_name)(self.args)

    def run(self):
        self.backend.initialize()
        print "Configuration written to " + config.local_config_filename()

init_parser = __register_command(InitializeCommand, help="Initialize a project")
init_subparser = init_parser.add_subparsers(dest="backend_name")

class ListCommand(Command):
    name = "list"
    options = [ ('state', { 'type' : str, 'default' : "open", 'choices' : ["open", "closed"], 'help' : 'State of issues to list (open or closed). Defaults to open if unspecified.' } ),
                ('limit', { 'type' : int, 'default' : None, 'help' : "Number of issues to list" } ),
                ('tag', { 'type' : str, 'default' : None, 'help' : "Tag to search for" } ),
                ]
    flags = [ ("mine", 'Display only issues for which I am the owner.'),
              ]

    date_format = "%Y/%m/%d"

    def run(self):
        filtered = self.args.mine or self.args.tag
        issues = []
        if filtered:
            issues = self.backend.filtered_issue_list(self.args.state, self.args.mine, self.args.tag)
        else:
            issues = self.backend.issue_list(self.args.state)
        self.print_issue_list(issues, self.args.limit)

    def __truncate_ljust_string(self, s, l, no_truncate=False):
        s = unicode(s)
        if len(s) <= l or no_truncate:
            return s.ljust(l)
        else:
            return s[0:l-3]+"..."

    def __format_issue_line(self, id, date, title, creator, owner, num_comments, is_title_line=False):
        if date.__class__ == str:
            date_str = date
        else:
            date_str = date.strftime(self.date_format)
        return id.ljust(6) + " " + self.__truncate_ljust_string(date_str,10) + "  " + self.__truncate_ljust_string(title, 35) + "  " + self.__truncate_ljust_string(creator,12) + "  " + self.__truncate_ljust_string(owner, 12) + self.__truncate_ljust_string(num_comments, 5, is_title_line)

    def __state(self):
        if (self.args.state == "open"):
            return True
        if (self.args.state == "closed"):
            return False

    def print_issue_list(self, issues, limit=None):
        """Print list of issues to stdout."""
        print self.__format_issue_line("ID", "date", "title", "creator", "owner", "# comments", True)
        if (limit is None):
            limit = len(issues)
        for i in issues[0:limit]:
            print self.__format_issue_line(i.id, i.create_time, i.title, i.creator, i.owner or "", i.num_comments)

list_parser = __register_command(ListCommand, help="Print a list of issues")

class ViewIssueCommand(Command):
    name = "show"
    required = [('id', { 'type' : str, 'help' : 'issue ID' }), ]

    def run(self):
        issue, comments = self.backend.get_issue(self.args.id)
        util.print_issue(issue, comments)

view_issue_parser = __register_command(ViewIssueCommand, help="Display an issue")

class AddIssueCommand(Command):
    name = "add"
    options = [ ('title', { 'type' : str, 'default' : None, 'help' : 'Title of issue.' } ),
                ('body', { 'type' : str, 'default' : None, 'help' : 'Body of issue.' } ),
                ('tags', { 'type' : str, 'default' : '', 'help' : 'List of tags for issue. A string, with tags separated by commas. E.g., "--tags=widgets,frobnicator"' }),
                ]

    def run(self):
        title, body = self.get_title_body()
        tags = [t for t in self.args.tags.split(",") if t] # Filter out any empty strings
        issue = self.backend.add_issue(title, body, tags=tags)
        print "Issue added!"
        print
        util.print_issue(issue[0], issue[1])

    def get_title_body(self):
        title = self.args.title or ""
        body = self.args.body or ""
        if (title == "" or body == ""):
            title, body, exit_status = util.get_title_body_from_editor(title, body, prefix='idli-add-issue')
            if (exit_status != 0):
                raise idli.IdliException("Operation cancelled.")
        return title, body

add_issue_parser = __register_command(AddIssueCommand, help="Display an issue")

class AddCommentCommand(Command):
    name = "comment"
    required = [('id', { 'type' : str, 'help' : 'issue ID' }), ]
    options = [ ('body', { 'type' : str, 'default' : None, 'help' : 'Body of issue.' } ),
                ]

    def run(self):
        issue = self.backend.get_issue(self.args.id) # Will raise error message if issue cannot be found
        message = self.args.body
        if (message is None):
            message, exit_status = util.get_string_from_editor("# Type your comment here.", prefix='idli-comment-')
            if (exit_status != 0):
                raise idli.IdliException("Operation cancelled.")
        self.backend.add_comment(self.args.id, message)
        print "Comment added!"
        print
        issue, comments = self.backend.get_issue(self.args.id)
        util.print_issue(issue, comments)

add_comment_parser = __register_command(AddCommentCommand, help="Comment on an issue")

class ResolveIssueCommand(Command):
    name = "resolve"
    options = [ ('state', { 'type':str, 'default': "closed", 'choices' : ["open", "closed"], 'help':'State of issues to list (open or closed)' } ),
                ('message', { 'type' : str, 'default' : None, 'help':'Resolution message.' } ),
                ]
    required = [ ('id', { 'type' :str, 'help' : "ID of issue." } ), ]

    def run(self):
        message = self.args.message
        message = self.args.message
        if (message is None):
            message, exit_status = util.get_string_from_editor("Issue resolved.\n# More details go here.", prefix='idli-resolve-')
        if (exit_status != 0):
            raise idli.IdliException("Operation cancelled.")
        issue = self.backend.resolve_issue(self.args.id, status = self.args.state, message = message)
        issue, comments = self.backend.get_issue(self.args.id)
        print "Issue state changed to " + str(self.args.state)
        print
        util.print_issue(issue, comments)

resolve_issue_parser = __register_command(ResolveIssueCommand, help="Resolve an issue")

class TagIssueCommand(Command):
    name = "tag"
    required = [ ('id', { 'type' : str, 'help' : "ID of issue." } ),
                 ('tags', { 'type' : str, 'help' : 'List of tags for issue. A string, with tags separated by commas. E.g., "widgets,frobnicator"' }),
                 ]
    flags = [ ("remove", 'If this flag is set, the tags will be removed instead of added.'),
              ]

    def run(self):
        issue, comments = self.backend.get_issue(self.args.id) # This will raise an error if the issue does not exist.
        tags = [t for t in (self.args.tags).split(",") if t] # Remove empty tags

        if self.args.remove: #If user asked to remove nonexistent tag, raise an error.
            for t in tags:
                if not (t in issue.tags):
                    raise idli.IdliException("The issue " + str(self.args.id) + " does not have the tag " + t + ". No action performed. Tags available: " + ", ".join(issue.tags))
                tags = [t for t in tags if not (t in issue.tags)]

        #Now actually tag the issue.
        self.backend.tag_issue(self.args.id, tags, self.args.remove)
        issue,comments = self.backend.get_issue(self.args.id)
        util.print_issue(issue, comments)

tag_issue_parser = __register_command(TagIssueCommand, help="Tag an issue")


class AssignIssueCommand(Command):
    name = "assign"
    options = [ ('message', { 'type' : str, 'default' : None, 'help' : 'Resolution message.' } ), ]
    required = [ ('id', { 'type' : str, 'help' : "ID of issue."}),
                 ('user', { 'type': str, 'help' :"username."})
                 ]

    def run(self):
        message = self.args.message
        if (message is None):
            message, exit_status = util.get_string_from_editor("Please resolve this issue.", prefix='idli-assign-')
        if (exit_status != 0):
            raise idli.IdliException("Operation cancelled.")
        issue = self.backend.assign_issue(self.args.id, user=self.args.user, message = message)
        issue, comments = self.backend.get_issue(self.args.id)
        print "Issue " + self.args.id + " assigned to " + unicode(self.args.user)
        print
        util.print_issue(issue, comments)

assign_issue_parser = __register_command(AssignIssueCommand, help="Assign issue to user.")

def run_command():
    parsed = main_parser.parse_args()
    cmd_arg = parsed.command
    command = commands[cmd_arg]
    command_runner = command(parsed)
    try:
        result = command_runner.run()
    except idli.IdliException, e:
        print e.value
