import toml


class ServerConfig:
    def __init__(self, opts) -> None:
        opts = opts["server"]
        self.host: str = opts["host"]
        self.port: int = opts["port"]

    @classmethod
    def load(cls, config_file):
        with open(config_file) as config:
            return cls(toml.load(config))
