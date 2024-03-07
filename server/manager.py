import secrets
from typing import Dict, List, Union
from database import Database
from typing import Union
import logging

logger = logging.getLogger("Manager")


class Manager:
    def __init__(self):
        self.tokens: Dict[str, Database] = {}

    def create(self) -> str:
        logger.info("Creating token")
        token: str = secrets.token_hex(16)
        self.tokens[token] = Database()
        return token

    def verify(self, token: str) -> bool:
        return self.tokens.get(token, None) is not None

    def execute(self, token: str, queryobj: Dict[str, Union[str, List[str]]]) -> Dict[str, Union[str, bytes]]:
        if not self.verify(token):
            return {"status": "ERR", "message": "invalid token"}

        try:
            result = self.tokens[token].query(queryobj)
            if result:
                return {"status": "OK", "result": result}
        except Exception as err:
            logger.error("Failed to execute command with %s", err)
            return {"status": "ERR", "message": repr(err)}

        return {"status": "OK"}

    def handle_query(self, data):
        keys = data.keys()
        try:
            if keys == {"create"}:
                return {"status": "OK", "token": self.create()}

            elif keys == {"token", "query"}:
                return self.execute(
                    data["token"],
                    data["query"]
                )
            else:
                return {"status": "ERR", "message": "invalid query"}

        except Exception as err:
            return {"status": "ERR", "message": err}
