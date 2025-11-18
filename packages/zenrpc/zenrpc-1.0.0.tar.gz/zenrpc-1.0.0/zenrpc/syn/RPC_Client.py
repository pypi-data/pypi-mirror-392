'''
Created on 20251114
Update on 20251115
@author: Eduardo Pagotto
'''

import logging
from sjsonrpc.syn import ProxyObject
from zenrpc.syn import ConnectionRemote

class RPC_Client(object):
    def __init__(self, addr) -> None:
        self.comm = ConnectionRemote(addr)
        self.log = logging.getLogger(__name__)

    def connect(self):
        self.comm.connect()

    def disconect(self):
        self.comm.disconnect()

    def __enter__(self):
        self.comm.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.comm.disconnect()
        if exc_type is not None:
            self.log.error(f"Uma exceção ocorreu no bloco 'async with': {exc_value}")
            return False

        return True # Retorna True se não houver exceção para indicar sucesso

    def call(self):
        return ProxyObject(self.comm)
