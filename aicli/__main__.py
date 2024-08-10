"""
AICLI  CLI for AI

this module is designed in the form of a CLI to make it easier to invoke AI API calls from other tools.

This file handles the execution when called with python -m aicli.

`python -m aicli <arg1> <arg2>`

"""
import aicli
from .main import main
from argparse import ArgumentParser

main()


