import bugger
import bugger.github as gh

backend = gh.GithubBackend("stucchio", "Test-repo")

def format_issue_line(id, date, title, creator, num_comments):
    if date.__class__ == str:
        date_str = date
    else:
        date_str = date.strftime("%Y/%m/%d %H:%M")
    return id.rjust(4) + ":" + date_str.ljust(16) + "  " + title.ljust(25) + "  " + creator.ljust(25) + "  " + str(num_comments).ljust(5)

def print_issue_list(backend, state=True, limit=-1):
    issues = backend.issue_list(state)
    if state:
        print "Open issues:"
    else:
        print "Closed issues:"
    print format_issue_line("ID", "date", "title", "creator", "# comments")
    for i in issues[0:limit]:
        print format_issue_line(i.hashcode, i.date, i.title, i.creator, i.num_comments)

if __name__ == "__main__":
    print_issue_list(backend, True, 20)

