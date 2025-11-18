'''
Created on 20251114
Update on 20251115
@author: Eduardo Pagotto
'''

import json
import logging
from urllib.parse import urlparse

from zencomm import ProtocolCode
from zencomm.asy import Protocol, socket_client

from sjsonrpc.asy import  ConnectionControl

from sjsonrpc.exceptjsonrpc import ExceptRPC

class ConnectionRemote(ConnectionControl):
    def __init__(self, url):
        super().__init__(url)
        self.log = logging.getLogger(__name__)
        self.protocol = None

    async def connect(self):

        if self.protocol:
            return

        try:
            self.log.info(f"connect to {self.getUrl()}")
            reader, writer = await socket_client(urlparse(self.getUrl()), 60)
            self.protocol = Protocol(reader, writer, 30)
            return

        except FileNotFoundError:
            self.log.error(f"socket not found at {self.getUrl()}")

        except ConnectionRefusedError:
            self.log.error(f"Connection to {self.getUrl()} refused.")

        except Exception as exp:
            self.log.error(f"Connection to {self.getUrl()} error: {str(exp)}")

        raise ExceptRPC('fail RCP access comunication')

    async def disconnect(self):
        if self.protocol:
            await self.protocol.sendClose('bye')
            self.protocol = None

    async def exec(self, input_rpc : dict, *args, **kargs) -> dict:

        await self.protocol.sendString(ProtocolCode.COMMAND, json.dumps(input_rpc))
        c, m = await self.protocol.receiveString()
        if c == ProtocolCode.RESULT:
            return json.loads(m)
        else:
            raise ExceptRPC(m)
