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
    print get_editor_name_as_list()
    exit_status = subprocess.call(get_editor_name_as_list() + [tf.name])
    result = tf.read()
    return (result, exit_status)

if __name__ == "__main__":
    result, es = get_string_from_editor("test\n\ntest 2 \n")
    print (result, es)

