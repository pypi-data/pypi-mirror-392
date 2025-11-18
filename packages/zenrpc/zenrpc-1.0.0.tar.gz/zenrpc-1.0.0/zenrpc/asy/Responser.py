'''
Created on 20251114
Update on 20251114
@author: Eduardo Pagotto
'''

import asyncio
import json
import logging
import threading
from sjsonrpc.asy import RPC_Responser

from zencomm import ProtocolCode, ExceptZen
from zencomm.asy import Protocol

class Responser(RPC_Responser):
    def __init__(self, target: object):
        super().__init__(target)
        self.log = logging.getLogger(__name__)

    async def __call__(self, *args, **kargs):
        """[execute exchange of json's messages with server RPC]
        """
        t_name = threading.current_thread().name
        self.log.info(f'start {t_name}')

        stop_event : asyncio.Event = args[0]

        protocol = None
        try:
            protocol = Protocol(args[1], args[2], 30)

        except Exception as exp:
            self.log.critical('fail creating connection: %s', str(exp))
            return

        count_to = 0

        while not stop_event.is_set():
            try:
                count_to = 0
                idRec, buffer = await protocol._receiveProtocol()
                if idRec == ProtocolCode.COMMAND:
                    await protocol.sendString(ProtocolCode.RESULT, json.dumps(await self.encode_exec_decode(json.loads(buffer.decode('UTF-8')))))

                elif idRec == ProtocolCode.CLOSE:
                    self.log.debug(f'responser receive {buffer.decode('UTF-8')}')
                    break

            except asyncio.TimeoutError:
                count_to += 1
                self.log.warning(f"timeout receiving: {count_to}")

            except asyncio.IncompleteReadError as ein:
                self.log.error(f"incomplete read: {str(ein)}")
                break

            except ExceptZen as exx:
                self.log.error(f"fail protocol {str(exx)}")
                break

            except Exception as exp:
                self.log.error('%s exception error: %s', t_name, str(exp))
                break

        await protocol.close()

        self.log.info(f'{t_name} finnished')
