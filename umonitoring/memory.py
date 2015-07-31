#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from umonitoring.commons import  executeCommand, toTxt, toFlatDict


class memory(object):
    def __init__(self):
        """
        Constructor
        :return:
        """
        self.cache = {}
        self.values = {}

    def getAllValues(self):
        """
        Get memory informations
        :return:
        """
        self.meminfo()

    def meminfo(self):
        cmd_result = os.popen('cat /proc/meminfo').read().splitlines()

        for line in cmd_result:
            columns = line.split()
            fieldname = columns[0][:-1].lower()

            value = columns[1]
            try:
                if columns[2] == 'kB':
                    value = int(value) * 1024
            except:
                pass

            keyname = 'memory.meminfo.%(fieldname)s' % locals()
            self.values[keyname] = value

        # Add custom fields
        try:
            self.values['memory.meminfo.freepercent'] = float(self.values['memory.meminfo.memfree']) / float(self.values['memory.meminfo.memtotal']) * 100
            self.values['memory.meminfo.usedpercent'] = 100 - self.values['memory.meminfo.freepercent']
        except:
            pass



if __name__ == '__main__':
    monit = memory()
    monit.getAllValues()
    print(toTxt(toFlatDict(monit.values)))

