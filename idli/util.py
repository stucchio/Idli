import os
import tempfile
import subprocess

def get_editor_name_as_list():
    return os.getenv("EDITOR", "vi").split()

def get_title_body_from_editor(title, body, prefix='idli-'):
    base_string = (title or "#The title of the issue goes here")
    base_string += "\n\n"
    base_string += (body or "#The rest of the file contains the body of the comment.")
    base_string += "\n# Any line beginning with a '#' is a comment and will not be added."
    result, exit_status = get_string_from_editor(base_string, prefix)
    lines = [l for l in result.split("\n") if (len(l) > 1 and l[0] != "#")]
    title = lines[0]
    body = "\n".join(lines[1:])
    return (title, body, exit_status)

def get_string_from_editor(base_string, prefix='idli-'):
    tf = tempfile.NamedTemporaryFile('w+b',prefix=prefix)
    tf.write(base_string)
    tf.seek(0)
    exit_status = subprocess.call(get_editor_name_as_list() + [tf.name])
    result = tf.read()
    return (result, exit_status)

def static_method(meth):
    def smeth(self, *args, **kwargs):
        return meth(*args, **kwargs)
    return smeth

def print_issue(issue, comments):
    print "ID: " + issue.id
    print "Title: " + issue.title
    print "Creator: " + issue.creator
    print "Create time: " + str(issue.create_time)
    print "Open: " + str(issue.status)
    if not (issue.owner is None):
        print "Owner: " + str(issue.owner)
    if (issue.tags):
        print "Tags: " + ", ".join(issue.tags)
    print
    print issue.body
    print

    if len(comments) > 0:
        print "Comments:"
    for c in comments:
        print
        if (c.title != "") and (not (c.title is None)):
            print "    Comment: " + str(c.title.__class__)
        print "    Author: " + c.creator
        print "    Date: " + str(c.date)
        print
        print "    " + c.body.replace("\n", "\n    ")

if __name__ == "__main__":
    result, es = get_string_from_editor("test\n\ntest 2 \n")
    print (result, es)

