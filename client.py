import socket
import threading


class Client:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_buf_size = 1024
        self.running = False

    def run(self):
        self.sock.connect((self.host, self.port))
        self.running = True
        self.send_thread = threading.Thread(target=self.send_thread_func)
        self.send_thread.start()
        while self.running:
            msg = self.sock.recv(self.recv_buf_size).decode()
            if msg == '':
                print('error')
                break
            if msg == 'QUITTED':
                break
            if msg[:3] == 'MSG':
                print(msg[4:])
        self.running = False
        self.quit()

    def quit(self):
        self.running = False
        self.send_thread.join()
        self.sock.send(b'QUIT')
        self.sock.close()

    def send_thread_func(self):
        while self.running:
            msg = input()
            if msg == '':
                continue
            if msg == 'q':
                self.sock.send(b'QUIT')
                self.running = False
            if msg[:5] == 'name ':
                self.sock.send(('NAME ' + msg[5:]).encode())
            self.sock.send(msg.encode())


if __name__ == '__main__':
    c = Client('localhost', 8080)
    try:
        c.run()
    except KeyboardInterrupt:
        pass
    finally:
        if c.running:
            c.quit()
