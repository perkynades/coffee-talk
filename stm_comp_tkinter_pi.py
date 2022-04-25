from tkinter import Tk
from stmpy import Driver, Machine
from client import Client

class CompCommunication:
    """Docstring"""
    def __init__(self):
        """Docstring"""
        self.user_list = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian", "Coffee machine", "Break Room", "Lunch Room", "Watercooler"]
        self.username = "Coffee machine"
        self.server = '192.168.254.18' #Define yourself
        self.client = None
        root = Tk()
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()*0.9
        root.destroy()

    def display_app(self):
        """Docstring"""

        #Add something that displays everyone in the callroom
        
        input("Press enter to join callroom...")
        self.join_callroom()

    def display_callroom(self):
        """Docstring"""

        try:
            self.client = Client(self.server, self.user_list, self.username, self.screen_width, self.screen_height, True)
            self.client.run()
            input("Press enter to leave callroom...")
            self.leave_callroom()
        except Exception as e:
            print("1.", e)
            self.leave_callroom()
        
    def refresh(self):
        """Docstring"""
        self.stm.send("refresh")

    def join_callroom(self):
        """Docstring"""
        self.stm.send("join_callroom")

    def leave_callroom(self):
        """Docstring"""
        if self.client:
            self.client.close()
        self.stm.send("leave_callroom")
    
    def print_message(self, tekst):
        """Docstring"""
        print(tekst)

# initial transition
t0 = {
    "source": "initial", 
    "target": "idle",
    "effect": "print_message('t0')"
}

t1 = {
    "trigger": "join_callroom",
    "source": "idle",
    "target": "in_callroom",
    "effect": "print_message('t1')"
}

t2 = {
    "trigger": "leave_callroom",
    "source": "in_callroom",
    "target": "idle",
    "effect": "print_message('t2')"
}

t3 = {
    "trigger": "refresh",
    "source": "idle",
    "target": "idle",
    "effect": "print_message('t3')"
}

idle = {"name": "idle", "entry": "display_app"}
in_callroom = {"name": "in_callroom", "entry": "display_callroom"}

comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2, t3], states=[idle, in_callroom,], obj=comp, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()
