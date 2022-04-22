import socket, struct, threading, pyaudio, audioop, numpy, tkinter, math, cv2

server_ip_def = '10.22.225.254' #Define yourself
logged_in_def = "Jonatan" #Define yourself
root = tkinter.Tk()
screen_width_def = root.winfo_screenwidth()
screen_height_def = root.winfo_screenheight() * 0.9
root.destroy()

class Client:
    """Docstring"""
    def __init__(self, server_ip, username, screen_width, screen_height):
        """Docstring"""
        self.user_list = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
        self.server_ip = server_ip
        self.username = username
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.users_in_call = set()
        self.user_size = struct.calcsize("H")
        self.refresh_windows = False
        self.input_sensitivity = 30


        self.handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.handshake_socket.connect((self.server_ip, 10000))

        self.video_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.video_socket.connect((self.server_ip, 9999))
        self.video_socket.settimeout(1)

        self.audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.audio_socket.connect((self.server_ip, 8999))

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
            message = f'u={self.username},a={self.audio_socket.getsockname()[0]}:{self.audio_socket.getsockname()[1]},v={self.video_socket.getsockname()[0]}:{self.video_socket.getsockname()[1]};'
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
            print("5.", e)
            self.video_socket.shutdown(socket.SHUT_RDWR)
            self.audio_socket.shutdown(socket.SHUT_RDWR)
            self.handshake_socket.close()
            self.video_socket.close()
            self.audio_socket.close()

    def send_video(self):
        """Docstring"""
        try:
            vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            vid.set(3, 640)
            vid.set(4, 480)
            while vid.isOpened():
                _ , frame = vid.read()
                _ , frame = cv2.imencode(".jpg", frame)
                frame = frame.tobytes()
                msg1 = b'0' + struct.pack("H",self.user_list.index(self.username)) + frame[:len(frame)//2]
                msg2 = b'1' + struct.pack("H",self.user_list.index(self.username)) + frame[len(frame)//2:]
                self.video_socket.send(msg1)
                self.video_socket.send(msg2)
        except Exception as e:
            print("1.",e)
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
                    data = data[self.user_size+1:]
                    user_video_data[user] = data
                else:
                    if user_video_data[user] and user in self.users_in_call:
                        data = user_video_data[user] + data[self.user_size+1:]
                        output = numpy.frombuffer(data, dtype="B")
                        output = output.reshape(output.shape[0], 1)
                        output = cv2.imdecode(output, cv2.IMREAD_COLOR)
                        cv2.imshow(user, output)
                        cv2.waitKey(1)
                    user_video_data[user] = None
        except Exception as e:
            print("2.", e)
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
            print("3.", e)
            self.stream_in.close()

    def recv_audio(self):
        """Docstring"""
        try:
            while True:
                audio_data = self.audio_socket.recv(4096)
                self.stream_out.write(audio_data)
        except Exception as e:
            print("4.", e)
            self.stream_out.close()

    def run(self):
        x1 = threading.Thread(target = self.send_video)
        x2 = threading.Thread(target = self.recv_video)
        x3 = threading.Thread(target = self.send_audio)
        x4 = threading.Thread(target = self.recv_audio)
        x5 = threading.Thread(target = self.handshake)
        x1.start()
        x2.start()
        x3.start()
        x4.start()
        x5.start()
        input("Press enter to shutdown... (temporary)")
        try:
            self.handshake_socket.shutdown(socket.SHUT_RDWR)
        except Exception as _:
            pass
        x1.join()
        x2.join()
        x3.join()
        x4.join()
        x5.join()
        print("SHUTDOWN SUCCESS")

if __name__ == '__main__':
    print("dum")
    client = Client(server_ip_def, logged_in_def, screen_width_def, screen_height_def)
    client.run()