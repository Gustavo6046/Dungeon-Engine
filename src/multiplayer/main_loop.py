import json
import socket
import connector
import ConfigParser
import sys
import time


class NoConfigurationError(BaseException):
    pass


class DMGPMultiplayer(object):
    def __init__(self, game):
        self.game = game
        self.configurations = ConfigParser.ConfigParser()
        self.configurations.read(sys.argv)
        self.port = self.configurations.getint("Network", "MinPort")
        self.use_ssl = self.configurations.getboolean("Network", "UseSSL")
        self.timeout = self.configurations.getfloat("Network", "Timeout")
        self.connector = connector.SocketHelper(
            port=self.port,
            use_ssl=self.use_ssl,
            timeout_seconds=self.timeout,
            helper_id="Dungeon Engine Connection @ Port " + str(self.configurations.getint("Network", "MinPort"))
        )
        self.connector.register_receive_function(self.parse_dmgp)

    def connect_to(self, ip, port):
        """Connects to a client in another address."""
        self.connector.connect(ip, port, self.use_ssl, self.timeout)

    def parse_dmgp(self, data, address, connector):
        """This is the funciton that parses DMGP data received via a client.
        It does not work alone; it is passed to the socket connector as a receiving function!"""
        pass
