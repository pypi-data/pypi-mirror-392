'''
Created on 20251115
Update on 20251115
@author: Eduardo Pagotto
'''

import logging
import time
from urllib.parse import urlparse

from zencomm import GracefulKiller
from zencomm.syn import socket_server, ServiceServer

from zenrpc.syn import Responser

class RPC_Server(object):
    def __init__(self, url: str, server_timeout : float, listerns: int):

        url_parser = urlparse(url)
        sock = socket_server(url_parser, server_timeout, listerns)

        self.log = logging.getLogger(__name__)
        self.killer = GracefulKiller()
        self.service = ServiceServer(sock, Responser(self))
        self.service.start()

    def execute(self):
        cycle = 0
        while not self.service.done:

            self.log.info('cycle:%d connections:%d', cycle, len(self.service.lista))
            cycle += 1
            time.sleep(5)

            self.service.garbage()

            if self.killer.kill_now is True:
                self.service.sock.close()
                self.service.stop()
                break

        self.service.join()
