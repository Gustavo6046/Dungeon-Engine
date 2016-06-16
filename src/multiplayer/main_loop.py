import json
import socket
import connector
import ConfigParser
import sys
import time


class NoConfigurationError(BaseException):
    pass


class DMGPMultiplayer(object):
    """The main class used for the multiplayer functionality of the engine."""

    def __init__(self, game):
        self.starting_time = time.time()
        self.game = game
        self.host_address = None
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

        self.connector.connect(
            ip,
            port,
            self.use_ssl,
            self.timeout,
            ["CONNECTEDCLIENTS " + " ".join(
                ["{}:{}".format(ip, port) for ip, port in [x.split(":") for x in self.connector.connections.keys()]])]
        )

    def parse_dmgp(self, data, address, unused):
        """This is the funciton that parses DMGP data received via a client.
        It does not work alone; it is passed to the socket connector as a receiving function!"""

        def send_back(data, blocking=True):
            self.connector.send_data(address, data, blocking)

        def send_to_all(data, blocking=True):
            for client in self.connector.connections.keys():
                self.connector.send_data(client, data, blocking)

        for line in data:
            if line == "":
                continue

            if line.upper().startswith("CONNECTEDCLIENTS "):
                for ip, port in [x.split(" ") for x in line.split(" ")[1:]]:
                    if "{}:{}".format(ip, port) not in self.connector.connections.keys():
                        self.connect_to(ip, port)
                        send_back("CONNECTEDTO {}:{}".format(ip, port))

            if line.upper().startswith("IAMHOST "):
                if self.host_address:
                    send_back("ERR HOST_EXISTING")

                else:
                    send_back("INFO HOST_SUCCESFULLY_DEFINED")
                    send_to_all("DEFHOST " + address)

            if line.upper().startswith("DEFHOST "):
                if self.host_address:
                    send_back("ERR HOST_EXISTING")

                else:
                    send_back("INFO HOST_SUCCESFULLY_DEFINED")

            if line.upper() == "AMIHOST":
                if self.host_address == address:
                    send_back("INFO IS_HOST TRUE")

                else:
                    send_back("INFO IS_HOST FALSE")

            if line.upper().startswith("CTCP"):
                ctcp = line.split(" ")[1]

                if ctcp.upper() == "WHOISHOST":
                    send_back("INFO HOST " + self.host_address)

                if ctcp.upper() == "TIME":
                    send_back("INFO TIME " + str(time.time()))

                if ctcp.upper() == "RUNTIME":
                    send_back("INFO RUNTIME " + str(time.time() - self.starting_time))

                if ctcp.upper() == "STARTTIME":
                    send_back("INFO STARTTIME " + str(self.starting_time))

                else:
                    send_back("ERR UNKNOWN_CTCP_TYPE")
