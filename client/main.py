import multiprocessing as mp
import secrets
import socket
import pickle
import time
from pprint import pprint

import ujson as json
import logging
from base64 import b64decode
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("Client")


class Client:
    def __init__(self, token=""):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.token = token

        self.connect(("localhost", 8888))

    def send(self, obj, token=True):
        if token:
            obj["token"] = self.token
        self.socket.send((json.dumps(obj) + "\r\n").encode())

    def recv(self, delim="\r\n") -> dict:
        bufsz = 2048
        buf = b""

        while True:
            recv = self.socket.recv(bufsz)
            buf += recv
            if len(recv) == bufsz and not recv.endswith(b"\r\n"):
                continue
            break

        return json.loads(buf.decode().strip())

    def connect(self, addr):
        self.socket.connect(addr)
        if self.token:
            return

        self.send({"create": ""}, token=False)

        resp = self.recv()
        if resp["status"] == "OK":
            logger.info("Obtained token %s", resp["token"])
            self.token = resp["token"]
        else:
            raise Exception("Could not obtain a token")

    def result(self, resp):
        if resp["status"] == "OK" and "result" in resp:
            return pickle.loads(b64decode(resp["result"]))

    def query(self, stmt, params, result=False):
        query = {"statement": stmt, "parameters": params}
        self.send({"query": query})

        if result:
            return self.result(self.recv())
        else:
            self.recv()


def worker(id, token, max_queries):
    t_start = time.perf_counter()
    c = Client(token)
    c.query("CREATE TABLE IF NOT EXISTS cache (key VARCHAR(5), val INT);", [])

    try:
        for q in range(max_queries):
            key = secrets.token_hex(5)
            value = time.time_ns() / 1000000
            c.query("INSERT INTO cache VALUES (?, ?);", [key, value])
    except Exception as err:
        logging.error("Error: %s", err)

    delta = time.perf_counter() - t_start
    objs = c.query("SELECT * FROM cache;", [], True)
    logging.info("%d | Took %.2f seconds for %d queries (%.2f/s)", id, delta, max_queries, max_queries / delta)
    logging.info("%d | %d objects in cache", id, len(objs))


if __name__ == "__main__":
    c = Client()
    token = c.token
    c.query("CREATE TABLE IF NOT EXISTS cache (key VARCHAR(5), val INT);", [])

    procs = 50
    args = []
    for p in range(procs):
        args.append([p+1, "", 100])

    with mp.Pool(procs) as pool:
        pool.starmap(worker, args)

# c = Client("8e3791904af2e8100abac9bac4a8c087")
# pprint(c.query("SELECT * FROM cache;", [], result=True))
