====
Idli
====
----------------------------------------
A command line interface to bug trackers
----------------------------------------

Introduction
============

Documentation is incomplete...


Motivation
----------
Idli is a command line interface to bug tracking tools. The goal is simple. To
add a bug to a project, you can visit your bug tracker's website and use the web
interface.

I (the author) prefer the command line::

    $ idli add --title "The frobnicator is broken." --body "The frobnicator does not frobnicate."


Installation
============


Usage
=====
Setting up an idli project
--------------------------

To begin, you need to initialize an idli project. The general format for doing this is::

    $ cd project_dir
    $ idli init BACKEND OPTION1 OPTION2

For example, if the project is hosted on github, you would use::

    $ idli init github idli stucchio

This would direct idli set your idli backend to my idli repository.

Some idli commands also require login information::

    $ idli config github USERNAME TOKEN

where TOKEN is the github API token (go to https://github.com/account and select "Account Admin").

The `idli config` command is used to configure global variables,
while `idli init` is used to configure a project.

Using
-----

To add a bug::

    $ idli add --title "title of bug" --body "body of bug."

To list existing bugs::

    $ idli list
    ID:date              title                      creator                    # comments
    11:<2010/09/21 03:26>  Frobnicator broken         stucchio                   0
    12:<2010/09/21 03:27>  Widgets full of beer       stucchio                   0
    13:<2010/09/21 03:27>  Documentation confusing    stucchio                   0

If the title and body are unspecified, idli will open an editor for you to type them.
The specific editor used can be configured via the EDITOR environment variable (note that
git uses the same variable).

To view a bug in more detail::

    $ idli show 11
    ID: 11
    Title: Frobnicator broken
    Creator: stucchio
    Create time: 2010-09-21 03:26:57
    Open: True

    So very broken.

To resolve a bug::

    $ idli resolve 11 --message "Issue resolved by fixing the frobnicator."

To assign a bug::

    $ idli assign 11 scotty "I need warp drive now."

Backends vary
~~~~~~~~~~~~~

Not all features work in all backends. Github, for example, does not support assigning
a bug to a user.

Backends
========

Github
------
Idli can connect to the bug tracker at github. To use, first you need
to configure idli with your github login information::

    $ idli config github USER TOKEN

Here, USER is your username and TOKEN is your github API token. The TOKEN
can be accessed by logging in to github, proceeding to https://github.com/account
and selecting "Account Admin".

This need only be done once per computer.

To initialize a github project::

    $ idli init github REPO OWNER

Here, REPO is the name of the repository (e.g., 'idli') and OWNER is the github
username of the project owner (e.g., 'stucchio').

If you wish to use a separate USER/TOKEN pair for a specific project, after calling
`idli init`, you can use::

    $ idli config --local-only USER TOKEN

This will set the USER/TOKEN for the current project only.

Trac
----
Trac is much the same is github, but with slightly different parameters::

    $ idli config trac USER PASSWORD
    $ idli init SERVER PATH

Setting up trac
~~~~~~~~~~~~~~~

Idli can be used with trac, but this requires the xmlrpc plugin for trac to be enabled.

First, the xmlrpc plugin for trac must be installed::

    $ easy_install -Z -U http://trac-hacks.org/svn/xmlrpcplugin/trunk

The website for the plugin is here: http://trac-hacks.org/wiki/XmlRpcPlugin

Then it must be enabled. This can be done by adding the following to your trac.ini file::

    [components]
    tracrpc.* = enabled

Lastly, xmlrpc permissions must be given to authenticated users::

    $ trac-admin TRAC_DIRECTORY permission add authenticated XML_RPC

Adding new backends
-------------------

New backends can be added to idli by subclassing idli.Backend. For example,
the GithubBackend has the following general structure:

    class GithubBackend(idli.Backend):
        name = "github"
        config_section = "Github"
        init_names = { "repo" : "Name of repository",
                       "owner" : "Owner of repository (github username).",
                       }
        config_names = [ ("user", "Github username"),
                         ("token", "Github api token. Visit https://github.com/account and select 'Account Admin' to view your token.")
                         ]

The `init_names` and `config_names` parameters are used to create the arguments for `idli init`
and `idli config` respectively. These parameters can be retrieved using self.get_config(name)
(i.e., in a GithubBackend method, one can call `self.get_config("repo")` to get the name of
the reposuitory).

Then, various specific methods must be build::

    def add_issue(self, title, body): #Adds issue
        ...Implementation details...

    def issue_list(self, state=True): #Returns a list of idli.Issue objects - state is whether they are open or closed
        ...Implementation details...

etc. For a full listing, see the file idli/__init__.py. Any method which raises an `IdliNotImplementedException`
must be overridden (if possible).

To report errors to the user, you should raise an `idli.IdliException("error message")` from within the backend::

    def issue_list(self, state=True):
        ...Implementation details...
        raise idli.IdliException("Github hates us!")

...More details...
