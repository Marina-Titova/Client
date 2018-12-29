import socket
import time

class ClientError(Exception):
    """Exception ClientError"""
    pass

class Client(object):
    """Class Client with methods: put, get"""
    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout

    def put(self, key, value, timestamp=None):
        timestamp = timestamp or str(int(time.time()))

        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                msg = f'put {key} {value} {timestamp}\n'
                sock.sendall(msg.encode('utf8'))
                acpt = sock.recv(1024).decode('utf8')

                if acpt == 'ok\n\n':
                    return {}

                if acpt == 'error\nwrong command\n\n':
                    raise ClientError

        except socket.error:
            raise ClientError

    def get(self, metric):
        
        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                sock.sendall(f'get {metric}\n'.encode('utf8'))
                acpt = sock.recv(1024).decode('utf8')

                if acpt == 'ok\n\n':
                    return {}

                if acpt == 'error\nwrong command\n\n':
                    raise ClientError

                msg_list = acpt[3:].split('\n')
                msg_list = msg_list[:-2]

                metrics = dict()
                for i in range(len(msg_list)):
                    msg_list[i] = msg_list[i].split(' ')
                    if msg_list[i][0] in metrics.keys():
                        n = 0
                        for tpl in metrics[msg_list[i][0]]:
                            if tpl[0] > int(msg_list[i][2]):
                                metrics[msg_list[i][0]].insert(n, (int(msg_list[i][2]), float(msg_list[i][1])))
                            elif tpl[0] < int(msg_list[i][2]) and n+1 == len(metrics[msg_list[i][0]]):
                                metrics[msg_list[i][0]].append((int(msg_list[i][2]), float(msg_list[i][1])))
                            else:
                                n += 1
                    else:
                        metrics[msg_list[i][0]] = [(int(msg_list[i][2]), float(msg_list[i][1]))]

                return metrics

        except socket.error:
            raise ClientError
