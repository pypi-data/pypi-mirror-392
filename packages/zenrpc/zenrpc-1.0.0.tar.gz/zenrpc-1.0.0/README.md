# ZenRPC
Json RPC Python server-client zencomm protocol syn and async<br>

Deps:
- [ZenComm](https://github.com/EduardoPagotto/zencomm): Binary sync/async protocol
- [sJsonRpc](https://github.com/EduardoPagotto/sJsonRpc): Json RPC 2.0

Example of classes to create RPC very fast/easy a RPC client and server:
- ./tests/async_client.py: Async zencomm(binary) Json RPC client
- ./tests/async_server.py: Async zencomm(binary) Json RPC Server
- ./tests/client.py: Sync zencomm(binary) Json RPC client
- ./tests/server.py: Sync zencomm(binary) Json RPC Server

Tests:
```bash
# Teminal B execute:
./tests/async_server.py
```

```bash
# Teminal B execute:
./tests/async_client.py
```
