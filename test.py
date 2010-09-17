#!/usr/bin/python

import bugger
import bugger.commands as cmds

import sys
import argparse

if __name__ == "__main__":
    import bugger.backends.github as gh
    backend = gh.GithubBackend("stucchio/Test-repo", ("stucchio", "4g9fWC1"))
    cmds.run_command(backend)



