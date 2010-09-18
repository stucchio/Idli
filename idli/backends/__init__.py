import github
import sys
import idli.config as cfg

backend_list = { "github" : github.GithubBackend,
                 }

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
