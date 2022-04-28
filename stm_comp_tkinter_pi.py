from tkinter import Label, Tk, StringVar
from socket import socket, AF_INET, SOCK_DGRAM
from stmpy import Driver, Machine
from client import Client
from server import Server

class CompCommunication:
    """Docstring"""
    def __init__(self):
        """Docstring"""
        self.user_list = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian", "Coffee machine", "Break Room", "Lunch Room", "Watercooler"]
        self.username = "Coffee machine"
        self.client = None
        self.label_var = None
        self.after_id = None

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        self.server_ip = sock.getsockname()[0]
        self.server = Server(self.server_ip)
        self.server.run()
        sock.close()
        
        self.root = Tk()
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()*0.8
        self.root.destroy()
        self.root = None

    def display_app(self):
        """Docstring"""
        self.root = Tk()
        self.root.focus_force()
        self.root.bind("<Key>", self.join_callroom) #Used instead of card reader which should be in real implementation of the system
        self.root.attributes('-topmost',True)
        self.root.title('Coffee talk - Raspberry PI application')
        self.root.geometry(f'400x400+{int(self.root.winfo_screenwidth() / 2)-200}+{int(self.root.winfo_screenheight() / 2)-200}')
        self.label_var = StringVar(value=f'Users currently in the {self.username} callroom:')
        users_label = Label(self.root, textvariable=self.label_var)
        users_label.pack()

        self.after_id = self.root.after(1, self.update_callroom_user_list)
        self.root.mainloop()

    def display_callroom(self):
        """Docstring"""
        try:
            self.client = Client(self.server_ip, self.user_list, self.username, self.screen_width, self.screen_height, True)
            self.client.run()
            input("Press enter to leave callroom...") #Used instead of card reader which should be in real implementation of the system
            self.leave_callroom()
        except Exception as _:
            self.leave_callroom()
        
    def update_callroom_user_list(self):
        """Docstring"""
        self.label_var.set(f'Users currently in the {self.username} callroom:'+"\n"+"\n".join(self.server.get_callroom_user_list()))
        self.after_id = self.root.after(5000, self.update_callroom_user_list)

    def join_callroom(self, event=None):
        """Docstring"""
        self.root.after_cancel(self.after_id)
        self.root.destroy()
        self.stm.send("join_callroom")

    def leave_callroom(self):
        """Docstring"""
        if self.client:
            self.client.close()
        self.stm.send("leave_callroom")
    
# initial transition
t0 = {
    "source": "initial", 
    "target": "idle"
}

t1 = {
    "trigger": "join_callroom",
    "source": "idle",
    "target": "in_callroom"
}

t2 = {
    "trigger": "leave_callroom",
    "source": "in_callroom",
    "target": "idle"
}

idle = {"name": "idle", "entry": "display_app"}
in_callroom = {"name": "in_callroom", "entry": "display_callroom"}

comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2], states=[idle, in_callroom,], obj=comp, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()
