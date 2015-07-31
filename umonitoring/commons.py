#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import shlex

import subprocess
from subprocess import PIPE


class TimeoutException(Exception):
    pass


NAGIOSSTATE = ['OK', 'WARNING', 'CRITICAL']


def toFlatDict(dictvalue):
    """
    Convert Tow level dict array in flat dict array
    :param dictvalue:
    :return:
    """

    keys = dictvalue.keys()
    todelete = []
    toadd = {}

    # Flat the dict array
    for key in keys:
        if isinstance(dictvalue[key],dict):
            subkeys = dictvalue[key]
            for subkey in subkeys:
                fullsubkey = '%(key)s.%(subkey)s' % locals()
                toadd[fullsubkey] = subkeys[subkey]
            todelete.append(key)

    # Add new key
    for key in toadd:
        dictvalue[key] = toadd[key]

    # Delete unused keys
    for key in todelete:
        del dictvalue[key]

    return dictvalue

def toTxt(dictvalue):
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
    return str(int(s, 16))


def executeCommand(cmd):
    cmdargs = shlex.split(cmd)
    p = subprocess.Popen(cmdargs, stdout=PIPE, stderr=PIPE)
    output, errors = p.communicate()
    if p.returncode:
        print('Failed running %s' % cmd)
        raise Exception(errors)
    return output.decode('utf-8')


def loadFromCache(cachefile):
    """
    Load JSON content from file
    :param cachefile:
    :return:
    """
    if cachefile is None:
        return None

    if not os.path.exists(cachefile):
        return None

    lines = open(cachefile).read()
    return json.loads(lines)


def saveToCache(cachefile, jsoncontent):
    """
    Save JSON content to file
    :param cachefile:
    :param jsoncontent:
    :return:
    """
    if cachefile is None:
        return

    with open(cachefile, 'w') as f:
        jsontext = json.dumps(
            jsoncontent, sort_keys=True,
            indent=4, separators=(',', ': ')
        )
        f.write(jsontext)
        f.close()
