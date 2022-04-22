import socket, threading, selectors, types

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(("8.8.8.8", 80))
host_ip = sock.getsockname()[0]
sock.close()
print('HOST IP:', host_ip)

handshake_selector = selectors.DefaultSelector()
handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
handshake_address = (host_ip, 10000)
handshake_socket.bind(handshake_address)
handshake_socket.listen()
handshake_selector.register(handshake_socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=None)

video_participant_addresses = set()
video_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
video_address = (host_ip, 9999)
video_socket.bind(video_address)

audio_participant_addresses = set()
audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
audio_address = (host_ip, 8999)
audio_socket.bind(audio_address)

def serve_handshake():
    """Docstring"""
    print("LISTENING FOR HANDSHAKE AT:", handshake_address)
    user_list = []
    while True:
        events = handshake_selector.select(timeout=None)
        for key, mask in events:
            s = key.fileobj
            if key.data is None:
                client_socket, addr = s.accept()
                print(f'GOT CONNECTION FROM: {addr[0]}:{addr[1]}')
                data = types.SimpleNamespace(addr=addr, username=None, audio=None, video=None, inb=b'', outb=b'')
                events = selectors.EVENT_READ | selectors.EVENT_WRITE
                handshake_selector.register(client_socket, events, data=data)
            else:
                data = key.data
                try:
                    if mask & selectors.EVENT_READ:
                        packet = s.recv(1024)
                        if not packet:
                            raise Exception("Connection closed")
                        data.inb += packet
                        if b';' in data.inb:
                            packet = data.inb[:data.inb.index(b';')+1].decode("utf-8")
                            data.username = packet[packet.index("u=")+2: packet.index(",a")] + ";"
                            if user_list:
                                if data.username in user_list:
                                    print(f'CLOSING CONNECTION FROM: {data.addr[0]}:{data.addr[1]} (USER ALREADY IN CALL)')
                                    handshake_selector.unregister(s)
                                    s.shutdown(socket.SHUT_RDWR)
                                    s.close()
                                    continue
                                data.outb += "".join(user_list).encode("utf-8")
                            data.audio = tuple([packet[packet.index("a=")+2:packet.index(",v")].split(":")[0], int(packet[packet.index("a=")+2:packet.index(",v")].split(":")[1])])
                            data.video = tuple([packet[packet.index("v=")+2:packet.index(";")].split(":")[0], int(packet[packet.index("v=")+2:packet.index(";")].split(":")[1])])
                            data.inb = data.inb[data.inb.index(b';')+1:]
                            video_participant_addresses.add(data.video)
                            audio_participant_addresses.add(data.audio)
                            for obj in handshake_selector.__dict__['_fd_to_key'].values():
                                if obj.data and obj.data.username != data.username:
                                    obj.data.outb += data.username.encode("utf-8")
                            user_list.append(data.username)
                    if mask & selectors.EVENT_WRITE and len(data.outb) > 0:
                        s.sendall(data.outb)
                        data.outb = b''
                except Exception as _:
                    print(f'LOST CONNECTION FROM: {data.addr[0]}:{data.addr[1]}')
                    video_participant_addresses.remove(data.video)
                    audio_participant_addresses.remove(data.audio)
                    user_list.remove(data.username)
                    for obj in handshake_selector.__dict__['_fd_to_key'].values():
                        if obj.data:
                            obj.data.outb += data.username.encode("utf-8")
                    handshake_selector.unregister(s)
                    s.close()

def serve_video():
    """Docstring"""
    print("LISTENING FOR VIDEO AT:", video_address)
    while True:
        data, address = video_socket.recvfrom(65000)
        if data:
            for participant_address in video_participant_addresses:
                if participant_address != address:
                    video_socket.sendto(data, participant_address)

def serve_audio():
    """Docstring"""
    print("LISTENING FOR AUDIO AT:", audio_address)
    while True:
        data, address = audio_socket.recvfrom(4096)
        if data:
            for participant_address in audio_participant_addresses:
                if participant_address != address:
                    audio_socket.sendto(data, participant_address)

if __name__ == '__main__':
    x1 = threading.Thread(target = serve_handshake)
    x2 = threading.Thread(target = serve_video)
    x3 = threading.Thread(target = serve_audio)
    x1.start()
    x2.start()
    x3.start()
    x1.join()
    x2.join()
    x3.join()
