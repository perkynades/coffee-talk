from tkinter import Label, Entry, messagebox, Button, Tk
from stmpy import Driver, Machine
from client import Client
import requests
import ast

class CompCommunication:
    """Docstring"""
    def __init__(self):
        """Docstring"""
        self.user_list = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian", "Coffee machine", "Break Room", "Lunch Room", "Watercooler"]
        self.server_list = ['192.168.1.228'] #Define yourself
        self.username = None
        self.server = None
        self.client = None
        self.root = None
        self.users_in_rooms = dict({
            "coffeeRoom" : []
        })

    def display_login(self):
        """Docstring"""
        print('display login')
        #Define root window
        self.root = Tk()
        self.root.attributes('-topmost',True)
        self.root.title('Coffee talk - Desktop application')
        self.root.geometry(f'400x100+{int(self.root.winfo_screenwidth() / 2)-200}+{int(self.root.winfo_screenheight() / 2)-50}')
        
        #Root window features
        my_label = Label(self.root, text="Enter name: ")
        my_label.pack()
        my_textbox = Entry(self.root, width=30)
        my_textbox.pack()
        my_button = Button(self.root, text="Login", command=lambda: self.login(my_textbox.get()))
        my_button.pack()

        #Main loop for tkinter
        self.root.mainloop()

    def display_app(self):
        """Docstring"""
        self.get_users_in_rooms()

        self.root = Tk()
        self.root.attributes('-topmost',True)
        self.root.title('Coffee talk - Desktop application')
        self.root.geometry(f'400x400+{int(self.root.winfo_screenwidth() / 2)-200}+{int(self.root.winfo_screenheight() / 2)-200}')

        #Root window features
        hello_label = Label(self.root, text="Welcome " + self.username)
        refresh_button = Button(self.root, text="Refresh", padx=10, pady=5, command = self.refresh)
        quit_button = Button(self.root, text="Sign out", padx=10, pady=5, command = self.signout)
        hello_label.grid(row=0, column=1)
        refresh_button.grid(row=1, column=0)
        quit_button.grid(row=1, column=1)

        #Room menu
        button_1 = Button(self.root, text="Join Coffee Room", padx=40, pady=10, command=lambda: self.join_callroom(0))
        button_2 = Button(self.root, text="Join Break Room", padx=40, pady=10, command=lambda: self.join_callroom(1))
        button_3 = Button(self.root, text="Join Lunch Room", padx=40, pady=10, command=lambda: self.join_callroom(2))
        button_4 = Button(self.root, text="Join Watercooler", padx=40, pady=10, command=lambda: self.join_callroom(3)) 
        button_1.grid(row=2, column=0)
        button_2.grid(row=2, column=1)
        button_3.grid(row=3, column=0)
        button_4.grid(row=3, column=1)

        self.create_users_in_room_label(self.root, self.users_in_rooms["coffeeRoom"], "coffee").grid(row=4, column=0)

        #Main loop for tkinter
        self.root.mainloop()

    def display_callroom(self):
        """Docstring"""
        self.client = None
        self.root = Tk()
        self.root.attributes('-topmost',True)
        self.root.title('Coffee talk - Desktop application')
        self.root.geometry(f'400x{int(self.root.winfo_screenheight()*0.1)}+{int(self.root.winfo_screenwidth() / 2)-200}+{int(self.root.winfo_screenheight()*0.85)}')
        call_label = Label(self.root, text="Call room")
        call_label.pack()
        leave_button = Button(self.root, text="End call", command = self.leave_callroom)
        leave_button.pack()
        try:
            self.client = Client(self.server, self.user_list, self.username, self.root.winfo_screenwidth(), self.root.winfo_screenheight()*0.8, False)
            self.client.run()
        except Exception as _:
            self.leave_callroom()
        
        #entry: display_welcome_msg, subscribe to mqtt
        #entry: display_callroom
        print('in callroom')

        #exit: unsubscribe mqtt
        self.root.mainloop()
        
    def login(self, username):
        """Docstring"""
        if username in self.user_list:
            self.username = username
            self.root.destroy()
            self.stm.send("valid")
        else:
            self.root.destroy()
            self.stm.send("invalid")
            messagebox.showerror("Error", "Login failed")
            return

    def signout(self):
        """Docstring"""
        self.username = None
        self.root.destroy()
        self.stm.send("logout")

    def refresh(self):
        """Docstring"""
        self.root.destroy()
        self.stm.send("refresh")
    
    def print_message(self, tekst):
        """Docstring"""
        print(tekst)

    def join_callroom(self, server_index):
        """Docstring"""
        self.server = self.server_list[server_index]
        self.root.destroy()
        self.stm.send("join_callroom")

    def leave_callroom(self):
        """Docstring"""
        self.server = None
        if self.client:
            self.client.close()
        self.root.destroy()
        self.stm.send("leave_callroom")

    # ------ UTILS FOR THE DESKTOP APP ------
    def get_users_in_rooms(self):
        try:
            req = requests.get("http://" + self.server_list[0] + ":8080/user_list/")
            in_room = ast.literal_eval(req.text)
            self.users_in_rooms['coffeRoom'] = [s.replace(';', '') for s in in_room]
        except Exception as e:
            pass
    
    def create_users_in_room_label(self, root, users_in_room, room):
        room_string = "Users in " + room +" room:\n"

        if users_in_room:
            return Label(root, text = room_string + '\n'.join(users_in_room))
        else:
            return Label(root, text = room_string + 'Room is empty')

# initial transition
t0 = {
    "source": "initial", 
    "target": "pre_login",
    "effect": "print_message('t0')"
}

t1 = {
    "trigger": "invalid",
    "source": "pre_login",
    "target": "pre_login",
    "effect": "print_message('t1')"
}

t2 = {
    "trigger": "valid",
    "source": "pre_login",
    "target": "idle",
    "effect": "print_message('t2')"
}

t3 = {
    "trigger": "join_callroom",
    "source": "idle",
    "target": "in_callroom",
    "effect": "print_message('t3')"
}

t4 = {
    "trigger": "leave_callroom",
    "source": "in_callroom",
    "target": "idle",
    "effect": "print_message('t4')"
}

t5 = {
    "trigger": "logout",
    "source": "idle",
    "target": "pre_login",
    "effect": "print_message('t5')"
}
t6 = {
    "trigger": "refresh",
    "source": "idle",
    "target": "idle",
    "effect": "print_message('t6')"
}

pre_login = {"name": "pre_login", "entry": "display_login"}
idle = {"name": "idle", "entry": "display_app"}
in_callroom = {"name": "in_callroom", "entry": "display_callroom"}

comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5, t6], states=[pre_login, idle, in_callroom,], obj=comp, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()
