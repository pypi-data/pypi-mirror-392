'''
Created on 20251114
Update on 20251115
@author: Eduardo Pagotto
'''

import json
import logging
import socket
import threading
from sjsonrpc.syn import RPC_Responser

from zencomm import ProtocolCode
from zencomm.syn import Protocol

class Responser(RPC_Responser):
    def __init__(self, target: object):
        super().__init__(target)
        self.log = logging.getLogger(__name__)

    def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """
        t_name = threading.current_thread().name
        self.log.info(f'start {t_name}')

        stop_event = args[2]

        protocol = None
        try:
            protocol = Protocol(args[0])

        except Exception as exp:
            self.log.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while not stop_event.is_set():
            try:
                count_to = 0
                idRec, buffer = protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    protocol.sendString(ProtocolCode.RESULT, json.dumps(self.encode_exec_decode(json.loads(buffer.decode('UTF-8')))))

                elif idRec == ProtocolCode.CLOSE:
                    self.log.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            except socket.timeout:
                count_to += 1
                self.log.warning(f"timeout receiving: {count_to}")

            except Exception as exp:
                self.log.error('%s exception error: %s', t_name, str(exp))
                break

        protocol.close()

        self.log.info(f'{t_name} finnished')
