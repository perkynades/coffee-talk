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
video_socket.setblocking(False)

audio_participant_addresses = set()
audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
audio_address = (host_ip, 8999)
audio_socket.bind(audio_address)
video_socket.setblocking(False)

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
                            packet = data.inb.decode("utf-8").split(",")
                            data.inb = b''
                            data.username = packet[2]
                            if user_list:
                                if data.username in user_list:
                                    print(f'CLOSING CONNECTION FROM: {data.addr[0]}:{data.addr[1]} (USER ALREADY IN CALL)')
                                    handshake_selector.unregister(s)
                                    s.shutdown(socket.SHUT_RDWR)
                                    s.close()
                                    continue
                                data.outb += "".join(user_list).encode("utf-8")
                            data.audio = tuple([packet[0].split(":")[0], int(packet[0].split(":")[1])])
                            data.video = tuple([packet[1].split(":")[0], int(packet[1].split(":")[1])])
                            audio_participant_addresses.add(data.audio)
                            video_participant_addresses.add(data.video)
                            for obj in handshake_selector.__dict__['_fd_to_key'].values():
                                if obj.data and obj.data.username != data.username:
                                    obj.data.outb += data.username.encode("utf-8")
                            user_list.append(data.username)
                    if mask & selectors.EVENT_WRITE and len(data.outb) > 0:
                        s.sendall(data.outb)
                        data.outb = b''
                except Exception as _:
                    print(f'LOST CONNECTION FROM: {data.addr[0]}:{data.addr[1]}')
                    audio_participant_addresses.remove(data.audio)
                    video_participant_addresses.remove(data.video)
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
        try:
            data, address = video_socket.recvfrom(65000)
            if data and address in video_participant_addresses:
                for participant_address in video_participant_addresses:
                    if participant_address != address:
                        video_socket.sendto(data, participant_address)
        except Exception as _:
            continue

def serve_audio():
    """Docstring"""
    print("LISTENING FOR AUDIO AT:", audio_address)
    while True:
        try:
            data, address = audio_socket.recvfrom(4096)
            if data and address in audio_participant_addresses:
                for participant_address in audio_participant_addresses:
                    if participant_address != address:
                        audio_socket.sendto(data, participant_address)
        except Exception as _:
            continue

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
