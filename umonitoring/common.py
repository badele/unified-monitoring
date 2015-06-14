#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shlex
import subprocess
from subprocess import PIPE

class TimeoutException(Exception):
	pass


def totxt(dictvalue):

    result = ''
    keys = dictvalue.keys()

    # Get max len keyname
    maxlen = 0
    for key in keys:
        maxlen = max(maxlen, len(key))

    for key in sorted(keys):
        keyname = key.ljust(maxlen)
        value = dictvalue[key]
        result += '%(keyname)s: %(value)s\n' % locals()

    return result


def hex2dec(s):
    return str(int(s,16))

def executeCommand(cmd):
    cmdargs = shlex.split(cmd)
    p = subprocess.Popen(cmdargs, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate()
    if p.returncode:
        print('Failed running %s' % cmd)
        raise Exception(errors)
    return output.decode('utf-8')
