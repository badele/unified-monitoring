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
    '01': 'ESTABLISHED',
    '02': 'SYN_SENT',
    '03': 'SYN_RECV',
    '04': 'FIN_WAIT1',
    '05': 'FIN_WAIT2',
    '06': 'TIME_WAIT',
    '07': 'CLOSE',
    '08': 'CLOSE_WAIT',
    '09': 'LAST_ACK',
    '0A': 'LISTEN',
    '0B': 'CLOSING'
}

def _ip(s):
    """
    Convert Hexadecimal IP to decimal IP address
    :param s: Hexadecimal IP
    :return: Decimal IP address
    """
    ip = [(hex2dec(s[6:8])),(hex2dec(s[4:6])),(hex2dec(s[2:4])),(hex2dec(s[0:2]))]
    return '.'.join(ip)

def _convert_ip_port(ip_port):
    """
    Convert Hexadecimal port to decimal port
    :param ip_port: Hexadecimal Port
    :return: Decimal port
    """
    host,port = ip_port.split(':')
    return _ip(host),hex2dec(port)


class net(object):
    def __init__(self):
        """
        Constructor
        :return:
        """
        self.cache = {}
        self.values = {}
        self.nettypes = ['tcp', 'udp', 'unix', 'raw']
        self.getcache()

    def getcache(self):
        """Get all informations and store in cache var"""
        # TCP, UDP, UNIX, etc ...
        for nettype in self.nettypes:
            self.cache[nettype] = self.executeCmd4Nettype(nettype, True)

        self.cache['socket'] = self.executeCmd4Nettype('sockstat')

    def getAllValues(self):
        """
        Get all network informations
        :return:
        """
        # TCP, UDP, UNIX, etc ...
        for nettype in self.nettypes:
            self.net_count(nettype)
            self.net_state(nettype)
            self.net_distinct_remoteip(nettype)

        self.net_socket_state()

    def net_count(self, nettype):
        """
        Get connexion count for nettype
        :param nettype: nettype [ TCP, UDP, UNIX, etc ...]
        :return:
        """
        """"""
        self.values['net.%(nettype)s.count' % locals()] = len(self.cache[nettype])

    def net_state(self, nettype):
        """
        Get a connexion state for nettype
        :param nettype: nettype [ TCP, UDP, UNIX, etc ...]
        :return:
        """
        if nettype == 'unix':
            return

        groupestate = Counter()
        for line in self.cache[nettype]:
            groupestate[line[3]] += 1

        keyname = 'net.%(nettype)s.state' % locals()
        self.values[keyname] = {}
        for key, statename in STATE.iteritems():
            self.values[keyname][statename] = groupestate[key]

    def net_distinct_remoteip(self, nettype):
        """
        Get a unique remote for nettype
        :param nettype: nettype [ TCP, UDP, UNIX, etc ...]
        :return:
        """
        if nettype == 'unix':
            return

        distinctip = Set()
        for line in self.cache[nettype]:
            remoteip = line[2].split(':')[0]
            distinctip.add(remoteip)

        keyname = 'net.%(nettype)s.remote.count' % locals()
        self.values[keyname] = len(distinctip)


    def net_socket_state(self):
        """
        Get socket stats
        :return:
        """
        for line in self.cache['socket']:
            fieldname = 'socket.%s' % line[0][:-1].lower()
            # Remove primary field
            line.pop(0)

            # Create the global fieldname
            varname = line[0]
            value = line[1]
            fullfieldname = "net.%(fieldname)s.%(varname)s" % locals()
            self.values[fullfieldname] = value

    def executeCmd4Nettype(self, nettype, removeheader=False):
        """
        Execute a network command for networking
        ex: cat /proc/net/tcp
        :param nettype: nettype [ TCP, UDP, UNIX, etc ...]
        :return: a cat /proc/net/xxx result
        """
        result = []
        cmdresult = executeCommand('cat /proc/net/%(nettype)s' % locals())

        # Replace multiple space by one space (for split)
        cmdresult = re.sub(r' +', ' ', cmdresult)
        lines = cmdresult.split('\n')

        # Remove header and end line
        if removeheader:
            lines.pop(0)

        while len(lines) > 0 and lines[len(lines) - 1] == '':
            lines.pop(len(lines) - 1)

        # Get result columns
        for line in lines:
            column = line.split()
            result.append(column)

        return result


if __name__ == '__main__':
    monit = net()
    monit.getAllValues()
    print totxt(monit.values)
