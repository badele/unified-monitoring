#!/usr/bin/env python
# -*- coding: utf-8 -*-

import select
import socket

import commons

class TimeoutException(Exception):
	pass

class haproxy(object):
    def __init__(self, socket=None, cachefile=None):
        """
        Constructor
        :return:
        """

        if socket is None:
            socket = '/var/run/haproxy.socket'

        if cachefile is None:
            cachefile = '/tmp/haproxy.cache'

        self.socket = socket
        self.cachefile = cachefile
        self.values = {}
        self.oldvalues = {}


    def execute_socket_command(self,command, timeout=200):
        """
        Connect to socket and execute command
        :param command:
        :param timeout:
        :return:
        """
        buffer = ""

        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(self.socket)

        client.send(command + "\n")

        running = True
        while(running):
            r, w, e = select.select([client,],[],[], timeout)

            if not (r or w or e):
                raise TimeoutException()

            for s in r:
                if (s is client):
                    buffer = buffer + client.recv(16384)
                    running = (len(buffer)==0)

        client.close()

        return (buffer.decode('utf-8').split('\n'))


    def getInfos(self):
        """
        Get global info
        :return:
        """
        results =  self.execute_socket_command("show info")
        for result in results:
            columns = result.split(":")
            if len(columns) == 2:
                name, value = columns[0].lower(), columns[1]
                keyname = 'haproxy.info.%s' % name
                self.values[keyname] = value

    def getBackend(self):
        """
        Get HA Proxy frontend & backend informations
        :return:
        """
        headkeynames = self.execute_socket_command("show stat")[0].split(',')

        self.oldvalues = commons.loadFromCache(self.cachefile)
        lines =  self.execute_socket_command("show stat")[1:]
        for line in lines:
            columns = line.split(",")

            if len(columns) == 63:
                # frontend or backend informations
                searchkeys = [
                    'qcur', 'qmax', 'scur', 'smax', 'slim', 'stot', 'bin', 'bout' ,'dreq', 'dresp',
                    'ereq', 'econ', 'eresp', 'wretr', 'wredis', 'status', 'weight' ,'act', 'bck', 'chkfail', 'chkdown',
                    'lastchg', 'downtime', 'qlimit', 'pid', 'iid','sid', 'throttle', 'lbtot', 'tracked', 'type', 'rate',
                    'rate_lim', 'rate_max', 'check_status', 'check_code', 'check_duration', 'hanafail','req_rate',
                    'req_rate_max', 'req_tot', 'cli_abrt', 'srv_abrt', 'comp_in', 'comp_out' ,'comp_byp', 'comp_rsp',
                    'lastsess', 'last_chk', 'last_agt', 'qtime', 'ctime','rtime', 'ttime'
                ]

                for searchkey in searchkeys:
                    idx = headkeynames.index(searchkey)
                    keyname = 'haproxy.%s.%s.%s' % (columns[0].lower(),columns[1].lower(), searchkey.lower())
                    value = columns[idx]

                    try:
                        self.values[keyname] = int(value)
                    except:
                        self.values[keyname] = "UNDEFINED"


                # Get state from frontend or backend
                states = {}
                errorskey = ['hrsp_1xx', 'hrsp_2xx', 'hrsp_3xx', 'hrsp_4xx', 'hrsp_5xx', 'hrsp_other']
                for searchkey in errorskey:
                    idx = headkeynames.index(searchkey)
                    value = columns[idx]

                    try:
                        states[searchkey] = int(value)
                    except:
                        states[searchkey] = "UNDEFINED"

                keyname = 'haproxy.%s.%s.states' % (columns[0].lower(),columns[1].lower())
                self.values[keyname] = states
                commons.saveToCache(self.cachefile, self.values)


    def getAllValues(self):
        """
        Get all values from HA Proxy
        :return:
        """
        self.getInfos()
        self.getBackend()

if __name__ == '__main__':
    monit = haproxy()
    monit.getAllValues()
    print commons.totxt(monit.values)

