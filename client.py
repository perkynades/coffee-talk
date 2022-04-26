import socket, struct, threading, pyaudio, audioop, numpy, math, cv2, time

class Client:
    """Docstring"""
    def __init__(self, server_ip, user_list, username, screen_width, screen_height, is_pi):
        """Docstring"""
        self.user_list = user_list
        self.server_ip = server_ip
        self.username = username
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.is_pi = is_pi
        self.users_in_call = set()
        self.user_size = struct.calcsize("H")
        self.refresh_windows = False
        self.input_sensitivity = 30

        self.users_data = None

        self.handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.handshake_socket.connect((self.server_ip, 10000))

        self.video_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.video_socket.connect((self.server_ip, 9999))
        self.video_socket.settimeout(1)

        self.audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.audio_socket.connect((self.server_ip, 8999))

        self.users_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.users_socket.connect((self.server_ip, 7999))

        p = pyaudio.PyAudio()
        self.stream_in = p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, input = True, frames_per_buffer = 2048)
        self.stream_out = p.open(format = pyaudio.paInt16, channels = 1, rate = 44100, output = True, frames_per_buffer = 2048)

    def setup_video_windows(self):
        """Docstring"""
        if self.users_in_call:
            users_per_row = 5
            height_index = -1
            window_height = math.floor(self.screen_height / math.ceil(len(self.users_in_call)/users_per_row))
            window_width = min(math.floor(self.screen_width / min(len(self.users_in_call), users_per_row)), math.floor(window_height/3)*4)
            for i, user in enumerate(self.users_in_call):
                if i % users_per_row == 0:
                    height_index += 1
                cv2.namedWindow(user, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(user, cv2.WND_PROP_TOPMOST, 1)
                cv2.resizeWindow(user, window_width, window_height)
                cv2.moveWindow(user, window_width*(i % users_per_row), window_height*height_index)

    def handshake(self):
        """Docstring"""
        try:
            message = f'{self.audio_socket.getsockname()[0]}:{self.audio_socket.getsockname()[1]},{self.video_socket.getsockname()[0]}:{self.video_socket.getsockname()[1]},{self.users_socket.getsockname()[0]}:{self.users_socket.getsockname()[1]},{self.username};'
            self.handshake_socket.sendall(message.encode("utf-8"))
            reply = b''
            while True:
                reply += self.handshake_socket.recv(1024)
                if b';' in reply:
                    usernames = reply.decode("utf-8").split(";")
                    reply = usernames.pop(-1).encode("utf-8")
                    for username in usernames:
                        if username in self.users_in_call:
                            self.users_in_call.remove(username)
                        else:
                            self.users_in_call.add(username)
                    self.refresh_windows = True
                elif not reply:
                    raise Exception("Connection closed")
        except Exception as e:
            print("1.", e)
            self.video_socket.shutdown(socket.SHUT_RDWR)
            self.audio_socket.shutdown(socket.SHUT_RDWR)
            self.users_socket.shutdown(socket.SHUT_RDWR)
            self.handshake_socket.close()
            self.video_socket.close()
            self.audio_socket.close()
            self.users_socket.close()

    def send_video(self):
        """Docstring"""
        try:
            if self.is_pi:
                vid = cv2.VideoCapture(0)
            else:    
                vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            vid.set(3, 640)
            vid.set(4, 480)
            prev = time.time()
            delay = 1/30
            while vid.isOpened():
                _ , frame = vid.read()
                if time.time() - prev > delay:
                    prev = time.time()
                    _ , frame = cv2.imencode(".jpg", frame)
                    frame = frame.tobytes()
                    msg1 = b'0' + struct.pack("H",self.user_list.index(self.username)) + frame[:len(frame)//2]
                    msg2 = b'1' + struct.pack("H",self.user_list.index(self.username)) + frame[len(frame)//2:]
                    self.video_socket.send(msg1)
                    self.video_socket.send(msg2)
        except Exception as e:
            print("2.",e)
            vid.release()

    def recv_video(self):
        """Docstring"""
        user_video_data = dict.fromkeys(self.user_list)
        try:
            while True:
                if self.refresh_windows:
                    self.refresh_windows = False
                    cv2.destroyAllWindows()
                    cv2.waitKey(1)
                    self.setup_video_windows()
                try:
                    data = self.video_socket.recv(65000)
                except socket.timeout as _:
                    continue
                index = data[:1]
                user = self.user_list[struct.unpack("H", data[1:self.user_size+1])[0]]
                if index == b'0':
                    user_video_data[user] = data[self.user_size+1:]
                else:
                    if user_video_data[user] and user in self.users_in_call:
                        data = user_video_data[user] + data[self.user_size+1:]
                        output = numpy.frombuffer(data, dtype="B")
                        output = output.reshape(output.shape[0], 1)
                        output = cv2.imdecode(output, 1)
                        cv2.imshow(user, output)
                        cv2.waitKey(1)
                    user_video_data[user] = None
        except Exception as e:
            print("3.", e)
            cv2.destroyAllWindows()
            cv2.waitKey(1)

    def send_audio(self):
        """Docstring"""
        try:
            while True:
                data = self.stream_in.read(2048)
                rms = audioop.rms(data, 2)
                if rms and 20*numpy.log10(rms) > self.input_sensitivity:
                    self.audio_socket.send(data)
        except Exception as e:
            print("4.", e)
            self.stream_in.close()

    def recv_audio(self):
        """Docstring"""
        try:
            while True:
                audio_data = self.audio_socket.recv(4096)
                self.stream_out.write(audio_data)
        except Exception as e:
            print("5.", e)
            self.stream_out.close()

    def send_users(self):
        try:
            while True:
                self.users_socket.send("get them users")
        except Exception as e:
            print("Lala")

    def recv_users(self):
        try:
            while True:
                self.users_data = self.users_socket.recv(4096)
                print(self.users_data)
        except Exception as e:
            print("nn")

    def get_users_list(self):
        self.x1 = threading.Thread(target = self.send_users)
        self.x2 = threading.Thread(target = self.recv_users)
        self.x1.start()
        self.x2.start()

    def run(self):
        """Docstring"""
        self.x1 = threading.Thread(target = self.send_video)
        self.x2 = threading.Thread(target = self.recv_video)
        self.x3 = threading.Thread(target = self.send_audio)
        self.x4 = threading.Thread(target = self.recv_audio)
        self.x5 = threading.Thread(target = self.handshake)
        self.x1.start()
        self.x2.start()
        self.x3.start()
        self.x4.start()
        self.x5.start()
    
    def close(self):
        """Docstring"""
        print("SHUTTING DOWN...")
        try:
            self.handshake_socket.shutdown(socket.SHUT_RDWR)
        except Exception as _:
            pass
        self.x1.join()
        self.x2.join()
        self.x3.join()
        self.x4.join()
        self.x5.join()
        print("SHUTDOWN SUCCESS")