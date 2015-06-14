#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Inspired by http://voorloopnul.com/blog/a-python-netstat-in-less-than-100-lines-of-code/

import re
import net
from collections import Counter
from sets import Set
import pprint


from common import  executeCommand, hex2dec, totxt

STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
        }

def _ip(s):
    ip = [(hex2dec(s[6:8])),(hex2dec(s[4:6])),(hex2dec(s[2:4])),(hex2dec(s[0:2]))]
    return '.'.join(ip)

def _convert_ip_port(ip_port):
    host,port = ip_port.split(':')
    return _ip(host),hex2dec(port)


class net(object):
    def __init__(self):
        self.cache = {}
        self.values = {}
        self.nettypes = ['tcp', 'udp', 'unix', 'raw']
        self.getcache()

    def getcache(self):
        """Get all informations and store in cache var"""
        # TCP, UDP, UNIX, etc ...
        for nettype in self.nettypes:
            self.cache[nettype] = self.executeNetSection(nettype)

    def getAllValues(self):
        # TCP, UDP, UNIX, etc ...
        for nettype in self.nettypes:
            self.net_count(nettype)
            self.net_state(nettype)
            if nettype != "unix":
                self.net_distinct_remoteip(nettype)

    def net_count(self, nettype):
        """Get a net type [ TCP, UDP, UNIX, etc ...]  connexion count"""
        self.values['%(nettype)s.count' % locals()] = len(self.cache[nettype])

    def net_state(self, nettype):
        groupestate = Counter()
        for line in self.cache[nettype]:
            groupestate[line[3]] += 1

        keyname = '%(nettype)s.state' % locals()
        self.values[keyname] = {}
        for key, statename in STATE.iteritems():
            self.values[keyname][statename] = groupestate[key]

    def net_distinct_remoteip(self, nettype):
        distinctip = Set()
        for line in self.cache[nettype]:
            remoteip = line[2].split(':')[0]
            distinctip.add(remoteip)

        keyname = '%(nettype)s.remote.count' % locals()
        self.values[keyname] = len(distinctip)


    def executeNetSection(self, section):
        result = []
        cmdresult = executeCommand('cat /proc/net/%(section)s' % locals())

        # Replace multiple space by one space (for split)
        cmdresult = re.sub(r' +', ' ', cmdresult)
        lines = cmdresult.split('\n')

        # Remove header and two end line
        lines.pop(0)
        lines.pop(len(lines)-1)
        if len(lines) > 1:
            lines.pop(len(lines)-1)

        # Get result columns
        for line in lines:
            column = line.split(' ')
            column.pop(0)
            result.append(column)

        return result


if __name__ == '__main__':
    monit = net()
    monit.getAllValues()
    print totxt(monit.values)
