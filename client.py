import socket, struct, threading, pyaudio, audioop, numpy, tkinter, math, cv2

root = tkinter.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight() * 0.9
root.destroy()

server_ip = '10.22.225.254' #Define yourself
input_sensitivity = 30 #Define yourself
logged_in = "Jonatan" #Define yourself
user_list = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
users_in_call = set()
user_size = struct.calcsize("H")
refresh_windows = False

handshake_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
handshake_socket.connect((server_ip, 10000))

video_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
video_socket.connect((server_ip, 9999))
video_socket.settimeout(1)

audio_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
audio_socket.connect((server_ip, 8999))

chunk = 2048
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream_in = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, input = True, frames_per_buffer = chunk)
stream_out = p.open(format = FORMAT, channels = CHANNELS, rate = RATE, output = True, frames_per_buffer = chunk)

def setup_video_windows():
    """Docstring"""
    if users_in_call:
        users_per_row = 5
        height_index = -1
        window_height = math.floor(screen_height / math.ceil(len(users_in_call)/users_per_row))
        window_width = min(math.floor(screen_width / min(len(users_in_call), users_per_row)), math.floor(window_height/3)*4)
        for i, user in enumerate(users_in_call):
            if i % users_per_row == 0:
                height_index += 1
            cv2.namedWindow(user, cv2.WINDOW_NORMAL)
            cv2.setWindowProperty(user, cv2.WND_PROP_TOPMOST, 1)
            cv2.resizeWindow(user, window_width, window_height)
            cv2.moveWindow(user, window_width*(i % users_per_row), window_height*height_index)

def handshake():
    """Docstring"""
    global refresh_windows
    try:
        message = f'u={logged_in},a={audio_socket.getsockname()[0]}:{audio_socket.getsockname()[1]},v={video_socket.getsockname()[0]}:{video_socket.getsockname()[1]};'
        handshake_socket.sendall(message.encode("utf-8"))
        reply = b''
        while True:
            reply += handshake_socket.recv(1024)
            if b';' in reply:
                usernames = reply.decode("utf-8").split(";")
                reply = usernames.pop(-1).encode("utf-8")
                for username in usernames:
                    if username in users_in_call:
                        users_in_call.remove(username)
                    else:
                        users_in_call.add(username)
                refresh_windows = True
            elif not reply:
                raise Exception("Connection closed")
    except Exception as e:
        print("5.", e)
        video_socket.shutdown(socket.SHUT_RDWR)
        audio_socket.shutdown(socket.SHUT_RDWR)
        handshake_socket.close()
        video_socket.close()
        audio_socket.close()

def send_video():
    """Docstring"""
    try:
        vid = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        vid.set(3, 640)
        vid.set(4, 480)
        while vid.isOpened():
            _ , frame = vid.read()
            _ , frame = cv2.imencode(".jpg", frame)
            frame = frame.tobytes()
            msg1 = b'0' + struct.pack("H",user_list.index(logged_in)) + frame[:len(frame)//2]
            msg2 = b'1' + struct.pack("H",user_list.index(logged_in)) + frame[len(frame)//2:]
            video_socket.send(msg1)
            video_socket.send(msg2)
    except Exception as e:
        print("1.",e)
        vid.release()

def recv_video():
    """Docstring"""
    global refresh_windows
    user_video_data = dict.fromkeys(user_list)
    try:
        while True:
            if refresh_windows:
                refresh_windows = False
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                setup_video_windows()
            try:
                data = video_socket.recv(65000)
            except socket.timeout as _:
                continue
            index = data[:1]
            user = user_list[struct.unpack("H", data[1:user_size+1])[0]]
            if index == b'0':
                data = data[user_size+1:]
                user_video_data[user] = data
            else:
                if user_video_data[user] and user in users_in_call:
                    data = user_video_data[user] + data[user_size+1:]
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

def send_audio():
    """Docstring"""
    try:
        while True:
            data = stream_in.read(chunk)
            rms = audioop.rms(data, 2)
            if rms and 20*numpy.log10(rms) > input_sensitivity:
                audio_socket.send(data)
    except Exception as e:
        print("3.", e)
        stream_in.close()

def recv_audio():
    """Docstring"""
    try:
        while True:
            audio_data = audio_socket.recv(4096)
            stream_out.write(audio_data)
    except Exception as e:
        print("4.", e)
        stream_out.close()

if __name__ == '__main__':
    x1 = threading.Thread(target = send_video)
    x2 = threading.Thread(target = recv_video)
    x3 = threading.Thread(target = send_audio)
    x4 = threading.Thread(target = recv_audio)
    x5 = threading.Thread(target = handshake)
    x1.start()
    x2.start()
    x3.start()
    x4.start()
    x5.start()
    input("Press enter to shutdown... (temporary)")
    try:
        handshake_socket.shutdown(socket.SHUT_RDWR)
    except Exception as _:
        pass
    x1.join()
    x2.join()
    x3.join()
    x4.join()
    x5.join()
    print("SHUTDOWN SUCCESS")