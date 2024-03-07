import logging
from typing import Dict, Union, Optional
from manager import Manager
from twisted.internet.protocol import Factory, Protocol
from twisted.protocols.basic import LineReceiver
from twisted.internet.interfaces import IAddress
import ujson as json

logger = logging.getLogger("Server")


class Server(LineReceiver):
    def __init__(self, manager):
        self.manager = manager
        super().__init__()

    def lineReceived(self, data: bytes) -> None:
        try:
            data = json.loads(data.decode('utf-8').strip())
        except json.JSONDecodeError as err:
            self.write({"status": "ERR", "message": "Unable to decode JSON"})
            logger.error("Failed to decode JSON %s", err)

        self.jsonReceived(data)

    def connectionMade(self):
        logger.info("Connection established")

    def connectionLost(self, reason) -> None:
        logger.info("Connection lost")

    def jsonReceived(self, data: Dict[str, Union[str, Dict[str, str]]]) -> None:
        self.write(self.manager.handle_query(data))

    def write(self, obj):
        self.transport.write(json.dumps(obj).encode() + self.delimiter)


class ServerFactory(Factory):
    def __init__(self, *args, **kw):
        self.manager = Manager()
        # super().__init__(self)

    def buildProtocol(self, addr: IAddress) -> Optional[Protocol]:
        return Server(self.manager)
