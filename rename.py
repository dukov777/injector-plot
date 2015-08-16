#!/usr/bin/env python

from time import *
import os


new_name = strftime("%d_%b_%H:%M:%S", localtime()) + "_out.msr"
os.rename("out.msr", new_name)
os.remove("latest.msr")
os.symlink(new_name, 'latest.msr')
 
 
