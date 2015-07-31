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
        df_result = os.popen('/bin/df -k -l -P ').read().splitlines()

        for line in df_result[1:]:
            result = line.split()
            keyname = 'df.%s' % result[5]
            self.values[keyname] = {}
            self.values[keyname]['filesystem'] = result[0]
            self.values[keyname]['totalsize'] = int(result[1]) * 1024
            self.values[keyname]['usersize'] = int(result[2]) * 1024
            self.values[keyname]['freesize'] = int(result[3]) * 1024
            self.values[keyname]['mountedpoint'] = result[5]
            self.values[keyname]['freepercent'] = self.values[keyname]['freesize'] / self.values[keyname]['totalsize'] * 100
            self.values[keyname]['usedpercent'] = self.values[keyname]['usersize'] / self.values[keyname]['totalsize'] * 100

if __name__ == '__main__':
    monit = disk()
    monit.getAllValues()
    print(toTxt(toFlatDict(monit.values)))

