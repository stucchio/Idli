import os
import tempfile
import subprocess

def get_editor_name_as_list():
    return os.getenv("EDITOR", "vi").split()

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

