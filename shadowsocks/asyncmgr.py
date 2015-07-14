__author__ = 'zhouqi'

import time
import os
import socket
import struct
import re
import logging
import common
import lru_cache
import eventloop
import server_pool
import Config

class ServerMgr(object):

    def __init__(self):
        self._loop = None
        self._sock = None

    def add_to_loop(self, loop):
        if self._loop:
            raise Exception('already add to loop')
        self._loop = loop
        # TODO when dns server is IPv6
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                   socket.SOL_UDP)
        self._sock.bind((Config.MANAGE_BIND_IP, Config.MANAGE_PORT))
        self._sock.setblocking(False)
        loop.add(self._sock, eventloop.POLL_IN)
        loop.add_handler(self.handle_events)

    def _handle_data(self, sock):
        data, addr = sock.recvfrom(128)
        #manage pwd:port:passwd:action
        args = data.split(':')
        if len(args) < 4:
            return
        if args[0] == Config.MANAGE_PASS:
            if args[3] == '0':
                server_pool.ServerPool.get_instance().cb_del_server(args[1])
            elif args[3] == '1':
                server_pool.ServerPool.get_instance().cb_new_server(args[1], args[2])

    def handle_events(self, events):
        for sock, fd, event in events:
            if sock != self._sock:
                continue
            if event & eventloop.POLL_ERR:
                logging.error('mgr socket err')
                self._loop.remove(self._sock)
                self._sock.close()
                # TODO when dns server is IPv6
                self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                           socket.SOL_UDP)
                self._sock.setblocking(False)
                self._loop.add(self._sock, eventloop.POLL_IN)
            else:
                self._handle_data(sock)
            break

    def close(self):
        if self._sock:
            self._sock.close()
            self._sock = None


def test():
    pass

if __name__ == '__main__':
    test()