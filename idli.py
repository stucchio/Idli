#!/usr/bin/python

import idli
import idli.commands as cmds

import sys
import argparse

if __name__ == "__main__":
    import idli.backends.github as gh
    backend = gh.GithubBackend("stucchio/Test-repo", ("stucchio", open("apitoken").read()))
    cmds.run_command(backend)



