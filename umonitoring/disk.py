#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from umonitoring.commons import  executeCommand, toTxt, toFlatDict



class disk(object):
    def __init__(self):
        """
        Constructor
        :return:
        """
        self.cache = {}
        self.values = {}

    def getAllValues(self):
        """
        Get disk informations
        :return:
        """
        self.get_df()

    def get_df(self):
        cmd_result = os.popen('/bin/df -k -l -P ').read().splitlines()

        for line in cmd_result[1:]:
            columns = line.split()
            keyname = 'disk.df.%s' % columns[5]
            self.values[keyname] = {}
            self.values[keyname]['filesystem'] = columns[0]
            self.values[keyname]['totalsize'] = int(columns[1]) * 1024
            self.values[keyname]['usedsize'] = int(columns[2]) * 1024
            self.values[keyname]['freesize'] = int(columns[3]) * 1024
            self.values[keyname]['mountedpoint'] = columns[5]
            self.values[keyname]['freepercent'] = self.values[keyname]['freesize'] / float(self.values[keyname]['totalsize']) * 100
            self.values[keyname]['usedpercent'] = self.values[keyname]['usedsize'] / float(self.values[keyname]['totalsize']) * 100

if __name__ == '__main__':
    monit = disk()
    monit.getAllValues()
    print(toTxt(toFlatDict(monit.values)))

