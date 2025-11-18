'''
Created on 20241001
Update on 20251114
@author: Eduardo Pagotto
'''

import asyncio

from zencomm.asy import SocketServer
from zenrpc.asy import Responser

class RPC_Server(object):
    def __init__(self, url: str):
        self.server = SocketServer(url, Responser(self))

    async def execute(self, stop_event:asyncio.Event):
        await self.server.execute(stop_event)

    # async def set_nome(self, nome: str):
    #     self.nome = nome

    # async def get_nome(self):
    #     return self.nome
