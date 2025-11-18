'''
Created on 20251114
Update on 20251115
@author: Eduardo Pagotto
'''

import logging
from sjsonrpc.asy import ProxyObject
from zenrpc.asy import ConnectionRemote

class RPC_Client(object):
    def __init__(self, addr) -> None:
        self.comm = ConnectionRemote(addr)
        self.log = logging.getLogger(__name__)

    async def connect(self):
        await self.comm.connect()

    async def disconect(self):
        await self.comm.disconnect()

    async def __aenter__(self):
        await self.comm.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, exc_tb):
        await self.comm.disconnect()
        if exc_type is not None:
            self.log.error(f"Uma exceção ocorreu no bloco 'async with': {exc_value}")
            return False

        return True # Retorna True se não houver exceção para indicar sucesso

    def call(self):
        return ProxyObject(self.comm)
