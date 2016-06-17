import errno
import socket
import ssl
import threading
import time


class ConnectionTerminated(BaseException):
    pass


class SocketConnector(object):
    def __init__(self, port, timeout_seconds=120, connection_messages=(), use_ssl=False):
        self.connections = {}
        self.our_port = port
        self.data_modifiers = []
        self.connection_messages = connection_messages
        self.timeout_seconds = timeout_seconds

        threading.Thread(name="Connector Listening Loop", target=self.listening_loop, args=(use_ssl,)).start()

    def register_sent_data_modifier(self, func):
        self.data_modifiers.append(func)

    def listening_loop(self, use_ssl=False):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listening_socket.bind(("localhost", self.our_port))
        listening_socket.listen(8)

        if use_ssl:
            ssl.wrap_socket(listening_socket)

        while True:
            try:
                (client, (ip, port)) = listening_socket.accept()

            except socket.error as error:
                if error.errno in (errno.EAGAIN, errno.EINPROGRESS, errno.EWOULDBLOCK):
                    continue

                print "Listening thread socket error! ({})".format(errno.errorcode[error.errno])
                return

            listening_socket.setblocking(False)

            self.connections["{}:{}".format(ip, port)] = {"socket": client, "ssl": use_ssl}
            listening_socket.settimeout(self.timeout_seconds)

            for message in self.connection_messages:
                self.send_data("{}:{}".format(ip, port), message)

            time.sleep(0.15)

    def connect(self, ip, port, our_port=8000, use_ssl=False):
        """Adds a connection to ip and our_port to the connections list.
        To access this address later, use the string key "<ip>:<our_port>" in the 'connections' dictionary."""

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if use_ssl:
            ssl.wrap_socket(new_socket)

        new_socket.bind(("localhost", our_port + 1 + len(self.connections)))

        while True:
            try:
                new_socket.connect((ip, port))

            except socket.error as error_code:
                if error_code.errno in (
                        errno.ECONNREFUSED,
                        errno.ECONNABORTED,
                        errno.EBUSY,
                        errno.ECONNRESET,
                        errno.EADDRNOTAVAIL,
                ):
                    print "Error connecting to {}:{}: Socket error! ({})".format(
                        ip,
                        port,
                        errno.errorcode[error_code.errno]
                    )
                    return False

                continue

            return True

        new_socket.setblocking(False)
        new_socket.settimeout(self.timeout_seconds)
        self.connections["{}:{}".format(ip, port)] = {"socket": new_socket, "ssl": use_ssl}

        for message in self.connection_messages:
            self.send_data("{}:{}".format(ip, port), message)

    def send_data(self, address, data, blocking=True):
        """Will handle sending data to the socket of corresponding address in the connections list."""

        try:
            for i, modifier in enumerate(self.data_modifiers):
                try:
                    data = modifier(data)

                except AttributeError:
                    print "Warning: Modifier at index {} isn't callable!".format(i)

        except (TypeError, ValueError):
            print "Warning: Invalid modifier value passed!"

        print "Sending \'{}\' to socket at address \'{}\'!".format(data, address)

        data += "\n"

        try:
            while True:
                bytes_sent = 0

                try:
                    bytes_sent += self.connections[address]["socket"].send(data[bytes_sent:])

                except socket.error as error_code:
                    if blocking:
                        print "Socket error: {}".format(errno.errorcode[error_code.errno])

                        if error_code.errno in (
                                errno.ECONNREFUSED, errno.ECONNABORTED, errno.ECONNRESET, errno.ETIMEDOUT):
                            print "Connection Error! Sending data to {} aborted! ({})".format(data, errno.errorcode(
                                error_code.errno))
                            raise ConnectionTerminated

                        if error_code.errno in (errno.EAGAIN, errno.EINPROGRESS, errno.EBUSY):
                            continue

                    else:
                        raise

                if bytes_sent == len(data):
                    return 0

        except KeyError:
            print "Warning: Address \'{}\' not found in connection list!".format(address)
            return 1

    def receive_data(self):
        """Will return a list of data received from all clients.
        Format: <ip>:<our_port> <data>"""

        data_received = {}

        for address, client in self.connections.items():
            def this_loop():
                current_data = ""
                while True:
                    try:
                        current_data += client.recv(4096)

                    except socket.error as error_code:
                        if error_code in (errno.ECONNREFUSED, errno.ECONNABORTED, errno.ECONNRESET, errno.ETIMEDOUT):
                            print "Connection Error! Receiving data from {} aborted! ({})".format(address,
                                                                                                  errno.errorcode(
                                                                                                      error_code.errno))
                            return 1

                        if error_code in (errno.EAGAIN, errno.EINPROGRESS):
                            continue

                    if not current_data.endswith("\n"):
                        continue

                    break

                return current_data

            current_data = this_loop()

            if current_data == 1:
                continue

            data_received[address] = current_data.split("\n")

        for address, items in data_received.items():
            for item in items:
                print "{} -- {}".format(address, item)

        return data_received


class SocketHelper(SocketConnector):
    """Helps connect with other sockets."""

    def __init__(
            self,
            port=8000,
            use_ssl=False,
            timeout_seconds=120,
            helper_id="DefaultSocketHelper",
            addresses=(),
            connection_messages=()
    ):
        """Initiates the helper.

        Arguments:
            -our_port: The minimum our_port that the sockets used will be bound to.
            -use_ssl: Whether the connections should use SSL.
            -timeout_seconds: The timeout of the connections.
            -helper_id: A ID to help identify the socket helper.
            -addresses: A iterator containing addresses with the <ip>:<our_port> format."""
        super(SocketHelper, self).__init__(port, timeout_seconds, connection_messages, use_ssl)
        self.receive_functions = []
        self.id = helper_id

        for address in addresses:
            ip, this_port = address.split(":")[:2]

            if not self.connect(ip, this_port, port, use_ssl):
                print "Connection to {}:{} failed!".format(ip, this_port)

    def start_loop(self, loop_time):
        """Starts the Receiving Loop which is a loop used to call the receiving functions every time any connection
        receives data from the other end."""
        threading.Thread(name="Helper {} Receiver".format(self.id), target=self.receiving_loop,
                         args=(loop_time,)).start()

    def register_receive_function(self, func):
        """Registers a receiving function, which is called with the arguments (address in format <ip>:<our_port>,
        list of data received, self)."""
        self.receive_functions.append(func)

    def receiving_loop(self, loop_time):
        """Do NOT call this directly! It will use up the entire current thread."""

        starting_time = time.time()

        try:
            while True:
                for address, data in self.receive_data():
                    for i, function in enumerate(self.receive_functions):
                        try:
                            function(address, data, self)

                        except AttributeError:
                            print "Invalid receiving function detected at index {} of helperID {}!".format(i, self.id)

                time.sleep(loop_time)

        finally:
            print "Loop ran for {} seconds!".format(time.time() - starting_time)
