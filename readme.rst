====
Idli
====
----------------------------------------
A command line interface to bug trackers
----------------------------------------

Introduction
============

Motivation
----------
Idli is a command line interface to bug tracking tools. The goal is simple. To
add a bug to a project, you can visit your bug tracker's website and use the web
interface.

Or you can simply type::
    $ idli add --title "The frobnicator is broken." --body "The frobnicator does not frobnicate."

Usage
=====

Setup
-----

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


