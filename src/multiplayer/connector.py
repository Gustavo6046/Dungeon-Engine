import errno
import ssl
import socket


class DMGPConnector(object):
    def __init__(self):
        self.connections = {}

    def connect(self, ip, port, use_ssl=False, timeout_seconds=120):
        """Adds a connection to ip and port to the connections list.
        To access this address later, use the string key "<ip>:<port>" in the 'connections' dictionary."""

        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if use_ssl:
            ssl.wrap_socket(new_socket)

        new_socket.bind(("localhost", int(open("port").read()) + len(self.connections)))
        new_socket.connect((ip, port))
        new_socket.setblocking(False)
        new_socket.settimeout(timeout_seconds)
        self.connections["{}:{}".format(ip, port)] = {"socket": new_socket, "ssl": use_ssl}

    def send_data(self, address, data, blocking=True, data_modifiers=()):
        """Will handle sending data to the socket of corresponding address in the connections list."""

        try:
            for modifier in data_modifiers:
                try:
                    data = modifier(data)

                except AttributeError:
                    print "Warning: Modifier {} isn't callable!".format(modifier.__name__)

        except (TypeError, ValueError):
            print "Warning: Invalid modifier value passed!"

        print "Sending \'{}\' to socket at address \'{}\'!".format(data, address)

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
                            print "Connection Error! Data sending aborted!"
                            return 1

                        if error_code.errno in (errno.EAGAIN, errno.EINPROGRESS, errno.EBUSY):
                            continue

                    else:
                        raise

                if bytes_sent == len(data):
                    return 0

        except KeyError:
            print "Warning: Address \'{}\' not found in connection list!".format(address)
            return 2

    def receive_data(self):
        """Will return a list of data received from all clients.
        Format: <ip>:<port> <data>"""
        # TO-DO: Make code for receiving protocol data from all other clients
        pass
