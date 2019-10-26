import socket
import threading
from time import sleep


class ClientThread(threading.Thread):
    def __init__(self, conn, info):
        threading.Thread.__init__(self)
        self.conn = conn
        self.info = info
        self.recv_buf_size = 1024
        self.panding = []

    def run(self):
        self.running = True
        while self.running:
            msg = self.conn.recv(self.recv_buf_size).decode()
            if msg == '':
                self.log('error')
                break
            if msg == 'QUIT':
                self.conn.send(b'QUITTED')
                self.log('quit')
                break
            self.log(f'received: {msg}')
            self.panding.append(msg)

    def tear(self):
        self.conn.close()

    def log(self, msg):
        print(f'{self.info}: {msg}')


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_max = 5
        self.threads = []
        self.refresh_rate = 0.2

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(self.listen_max)
        self.running = True
        self.broadcast_panding_thread = threading.Thread(target=self.broadcast_panding)
        self.broadcast_panding_thread.start()
        while self.running:
            conn, info = self.sock.accept()
            print(f'accepted connection from {info}')
            self.threads.append(ClientThread(conn, info))
            self.threads[-1].start()
        self.quit()

    def quit(self):
        self.broadcast_panding_thread.join()
        for t in self.threads:
            t.join()
        self.sock.close()

    def broadcast_panding(self):
        while self.running:
            self.threads = [t for t in self.threads if t.isAlive]
            for t in self.threads:
                for msg in t.panding:
                    for c in self.threads:
                        if c == t:
                            continue
                        c.conn.send(msg.encode())
            sleep(self.refresh_rate)





if __name__ == '__main__':
    s = Server('localhost', 8080)
    try:
        s.run()
    except KeyboardInterrupt:
        print('quit')
    except Exception as e:
        print(e)
    finally:
        s.quit()
