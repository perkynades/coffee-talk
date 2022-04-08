from stmpy import Driver, Machine
from tkinter import *

def validate_ID(id_name):
    names = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
    if id_name in names:
        return True
    return False

#Signout function
def signout():
    root.destroy()
    #idle()

#Refresh function
def refresh():
    print("refresh")

print('hei')

class CompCommunication:
    def idle(self):
        hello_label = Label(root, text="Welcome " + myTextbox.get())
        refreshButton = Button(root, text="Refresh", command = refresh)
        quitButton = Button(root, text="Sign out", command = signout)
        myLabel.destroy()
        myTextbox.destroy()
        myButton.destroy()
        hello_label.pack()
        refreshButton.pack()
        quitButton.pack()
        

    def pre_login(self):
        print('pre login')
        global root, myLabel, myButton, myTextbox
        #Define root window
        root = Tk()
        root.title('Coffee talk - Desktop application')
        root.geometry("400x100")
        #Root window features
        myLabel = Label(root, text="Enter name: ")
        myLabel.pack()
        myTextbox = Entry(root, width=30)
        myTextbox.pack()
        myButton = Button(root, text="Login", command= self.stm.send("press_login"))
        myButton.pack()

        #Main loop for tkinter
        root.mainloop()

    def in_callroom(self):
        #entry: display_welcome_msg, subscribe to mqtt
        #entry: display_callroom
        print('in callroom')
        #exit: unsubscribe mqtt
        return

    
    def check_ID(self):
        print('in check id')
        global id_name
        id_name = myTextbox.get()
        global wrong_label
        if validate_ID(id_name):
            print('id valid')
            self.stm.send("ID_valid")
            #loggedin()
            #videostream()
            #mqtt()
            #send to in_callroom
        else:
            print('id invalid')
            wrong_label.pack()
            root.after(1000, lambda: wrong_label.destroy())
            self.stm.send("ID_invalid")
            #send to back to idle
            return

# initial transition
t0 = {
    "source": "initial", 
    "target": "pre_login"
}

t1 = {
    "trigger": "press_login",
    "source": "pre_login", 
    "target": "check_ID"
}

t2 = {
    "trigger": "id_invalid",
    "source": "check_ID",
    "target": "pre_login",
    #"effect": "display_error"
}

t3 = {
    "trigger": "id_valid",
    "source": "check_ID",
    "target": "idle",
    #"effect": "display_welcome"
}

t4 = {
    "trigger": "join_callroom",
    "source": "idle",
    "target": "in_callroom",
    #"effect": "display_call"
}

t5 = {
    "trigger": "leave_callroom",
    "source": "in_callroom",
    "target": "idle",
    #"effect": "display_goodbye"
}

t5 = {
    "trigger": "logout",
    "source": "idle",
    "target": "pre_login",
    #"effect": "display_logout"
}

idle = {"name": "idle", "entry": "display_website"}
pre_login = {"name": "pre_login", "entry": "display_website"}
in_callroom = {"name": "in_callroom", "entry": "subscribe_mqtt, display_callroom"}
check_ID = {"name": "check_ID", "entry": "id_valid"}




comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2, t3, t4], states=[idle, in_callroom, check_ID], obj=comp, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()