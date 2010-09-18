#!/usr/bin/python

import idli
import idli.commands as cmds

import sys
import argparse

if __name__ == "__main__":
    from idli.backends import get_backend_or_fail
    cmds.run_command()



