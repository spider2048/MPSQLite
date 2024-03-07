import argparse
from models.config import ServerConfig
from server import ServerFactory
from twisted.internet import endpoints, reactor
import logging
logging.basicConfig(level=logging.DEBUG)


def main(args):
    config: ServerConfig = ServerConfig.load(args.config)
    endpoints.serverFromString(reactor, f"tcp:{config.port}").listen(ServerFactory())
    reactor.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config", help="path to config file", required=True)
    args = parser.parse_args()

    main(args)