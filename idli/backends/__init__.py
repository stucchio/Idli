import github
import trac
import sys
import idli.config as cfg
from idli.commands import configure_subparser, init_subparser

backend_list = { }

def register_backend(backend):
    #We must add parser options for each of init_names
    config_parser = configure_subparser.add_parser(backend.name, help="Configure " + backend.name + " backend.")
    __add_items_to_parser(backend.config_names, config_parser)
    init_parser = init_subparser.add_parser(backend.name, help="Configure " + backend.name + " backend.")
    __add_items_to_parser(backend.init_names, init_parser)

    backend_list[backend.name] = backend

def __add_items_to_parser(items, parser):
    if items.__class__ == dict:
        for (cmd, help) in items.iteritems():
            parser.add_argument(cmd, help=help)
    if items.__class__ == list:
        for (cmd, help) in items:
            parser.add_argument(cmd, help=help)


def get_backend_or_fail(backend_name = None):
    try:
        backend_name = backend_name or cfg.get_config_value("project", "type").lower()
        return backend_list[backend_name]
    except cfg.IdliMissingConfigException, e:
        print "Could not find idli configuration file. Run 'idli init' in the project root directory."
        sys.exit(0)
    except KeyError, e:
        print "No such backend '" + cfg.get_config_value("project", "type") + ". Check the configuration file " + cfg.local_config_filename() + " for errors."
        sys.exit(0)
    except Exception, e:
        print "Failed: " + str(e)
        sys.exit(0)

register_backend(github.GithubBackend)
register_backend(trac.TracBackend)
