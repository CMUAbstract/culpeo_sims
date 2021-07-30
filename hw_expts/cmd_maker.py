# Makes the commands for running loadProfiling.c
# sets up bash commands that will interact with the Makefile in this directory

import sys
import os

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class make_cmd():
    def __init__(self,home,appdir,flags):
        self.home = home
        self.appdir = appdir
        self.flags = flags

    def cd_cmd(self):
        script1 = "cd " + self.home + "/ ;"
        return script1

    def clean_cmd(self):
        script2 = "make clean ;"
        return script2

    def prog_cmd(self):
        script2 = "mspdebug tilib 'prog main.out' ;"
        return script2

    def bld_all_cmd(self):
        script2 = "make all "
        script3 = self.flags + ";"
        return script2 + script3


def gen_flags(*argv):
  flag_str =""
  if len(argv) % 2:
    return flag_str
  for i in range(0,len(argv),2):
    flag_str = flag_str + argv[i] + argv[i+1] + " "
  return flag_str

