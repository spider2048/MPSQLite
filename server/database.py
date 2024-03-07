import pickle
import sqlite3
import logging
from typing import Any, List, Dict, Optional, Union
from base64 import b64encode

logger = logging.getLogger("Database")


class Database:
    def __init__(self):
        self._db = sqlite3.connect(":memory:")
        self._cursor = self._db.cursor()
        self._optimize()

        logger.info("Created and optimized database")

    def _optimize(self):
        stmts = """PRAGMA journal_mode = WAL;PRAGMA busy_timeout = 5000;PRAGMA synchronous =
        NORMAL;PRAGMA cache_size = 1000000000;PRAGMA foreign_keys = true;PRAGMA temp_store = memory;"""
        for stmt in stmts.split(";"):
            self._cursor.execute(stmt)

    def commit(self):
        self._db.commit()

    def query(self, queryobj: Dict[str, Union[str, List[str]]]) -> Optional[str]:
        if queryobj.keys() != {"statement", "parameters"}:
            return None

        result = self._query(queryobj["statement"], queryobj["parameters"]).fetchall()
        if result:
            return b64encode(
                pickle.dumps(result)
            ).decode()

    def _query(self, query: str, params: List[Any]) -> Any:
        return self._cursor.execute(query, params)
