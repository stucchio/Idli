import github
import trac
import sys
import idli.config as cfg
from idli.commands import configure_subparser, init_subparser

backend_list = { }

def register_backend(backend):
    #We must add parser options for each of init_names
    config_parser = configure_subparser.add_parser(backend.name, help="Configure " + backend.name + " backend.")
    for (cmd, help) in backend.config_names.iteritems():
        config_parser.add_argument(cmd, help=help)
    init_parser = init_subparser.add_parser(backend.name, help="Configure " + backend.name + " backend.")
    for (cmd, help) in backend.init_names.iteritems():
        init_parser.add_argument(cmd, help=help)

    backend_list[backend.name] = backend

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
