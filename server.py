import socket, threading, selectors, types

class Server:
    """Docstring"""
    def __init__(self, host_ip):
        self.host_ip = host_ip
        self.user_list = []
        self.handshake_selector = selectors.DefaultSelector()
        self.handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.handshake_socket.bind((self.host_ip, 10000))
        self.handshake_socket.listen()
        self.handshake_selector.register(self.handshake_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

        self.video_participant_addresses = set()
        self.video_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.video_socket.bind((self.host_ip, 9999))
        self.video_socket.setblocking(False)

        self.audio_participant_addresses = set()
        self.audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.audio_socket.bind((self.host_ip, 8999))
        self.video_socket.setblocking(False)

        self.users_participant_addresses = set()
        self.users_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.users_socket.bind((self.host_ip, 7999))
        self.users_socket.setblocking(False)

    def serve_handshake(self):
        """Docstring"""
        print("LISTENING FOR HANDSHAKE AT:", (self.host_ip, 10000))
        while True:
            events = self.handshake_selector.select(timeout=None)
            for key, mask in events:
                s = key.fileobj
                if key.data is None:
                    client_socket, addr = s.accept()
                    print(f'GOT CONNECTION FROM: {addr[0]}:{addr[1]}')
                    data = types.SimpleNamespace(addr=addr, username=None, audio=None, video=None, users=None, inb=b'', outb=b'')
                    events = selectors.EVENT_READ | selectors.EVENT_WRITE
                    self.handshake_selector.register(client_socket, events, data=data)
                else:
                    data = key.data
                    try:
                        if mask & selectors.EVENT_READ:
                            packet = s.recv(1024)
                            if not packet:
                                raise Exception("Connection closed")
                            data.inb += packet
                            if b';' in data.inb:
                                packet = data.inb.decode("utf-8").split(",")
                                data.inb = b''
                                data.username = packet[3]
                                if self.user_list:
                                    if data.username in self.user_list:
                                        print(f'CLOSING CONNECTION FROM: {data.addr[0]}:{data.addr[1]} (USER ALREADY IN CALL)')
                                        self.handshake_selector.unregister(s)
                                        s.shutdown(socket.SHUT_RDWR)
                                        s.close()
                                        continue
                                    data.outb += "".join(self.user_list).encode("utf-8")
                                data.audio = tuple([packet[0].split(":")[0], int(packet[0].split(":")[1])])
                                data.video = tuple([packet[1].split(":")[0], int(packet[1].split(":")[1])])
                                data.users = tuple([packet[2].split(":")[0], int(packet[2].split(":")[1])])
                                self.audio_participant_addresses.add(data.audio)
                                self.video_participant_addresses.add(data.video)
                                self.users_participant_addresses.add(data.users)
                                for obj in self.handshake_selector.__dict__['_fd_to_key'].values():
                                    if obj.data and obj.data.username != data.username:
                                        obj.data.outb += data.username.encode("utf-8")
                                self.user_list.append(data.username)
                        if mask & selectors.EVENT_WRITE and len(data.outb) > 0:
                            s.sendall(data.outb)
                            data.outb = b''
                    except Exception as _:
                        print(f'LOST CONNECTION FROM: {data.addr[0]}:{data.addr[1]}')
                        self.audio_participant_addresses.remove(data.audio)
                        self.video_participant_addresses.remove(data.video)
                        self.users_participant_addresses.remove(data.users)
                        self.user_list.remove(data.username)
                        for obj in self.handshake_selector.__dict__['_fd_to_key'].values():
                            if obj.data:
                                obj.data.outb += data.username.encode("utf-8")
                        self.handshake_selector.unregister(s)
                        s.close()

    def serve_video(self):
        """Docstring"""
        print("LISTENING FOR VIDEO AT:", (self.host_ip, 9999))
        while True:
            try:
                data, address = self.video_socket.recvfrom(65000)
                if data and address in self.video_participant_addresses:
                    for participant_address in self.video_participant_addresses:
                        if participant_address != address:
                            self.video_socket.sendto(data, participant_address)
            except Exception as _:
                continue

    def serve_audio(self):
        """Docstring"""
        print("LISTENING FOR AUDIO AT:", (self.host_ip, 8999))
        while True:
            try:
                data, address = self.audio_socket.recvfrom(4096)
                if data and address in self.audio_participant_addresses:
                    for participant_address in self.audio_participant_addresses:
                        if participant_address != address:
                            self.audio_socket.sendto(data, participant_address)
            except Exception as _:
                continue
    
    def serve_users(self):
        """Docstring"""
        print("LISTENING FOR USERS REQUEST AT:", (self.host_ip, 7999))
        while True:
            try: 
                data, address = self.users_socket.recvfrom(4096)
                self.users_socket.sendto(self.user_list, address)
            except Exception as _:
                continue

    def run(self):
        """Docstring"""
        x1 = threading.Thread(target = self.serve_handshake)
        x2 = threading.Thread(target = self.serve_video)
        x3 = threading.Thread(target = self.serve_audio)
        x4 = threading.Thread(target = self.serve_users)
        x1.start()
        x2.start()
        x3.start()
        x4.start()

    def get_connected_users(self):
        """Docstring"""
        return self.user_list
