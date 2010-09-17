#!/usr/bin/python

import bugger
import bugger.commands as cmds

import sys
import argparse

if __name__ == "__main__":
    import bugger.github as gh
    backend = gh.GithubBackend("stucchio", "Test-repo")
    cmds.run_command(backend)



