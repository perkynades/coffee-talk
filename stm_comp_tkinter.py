from tkinter import messagebox
from stmpy import Driver, Machine
from tkinter import *
import threading

def validate_ID(id_name):
    names = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
    if id_name in names:
        return True
    return False




#Refresh function
def refresh():
    print("refresh")

class CompCommunication:
    #def idle(self):

    def display_app(self):
        print("Display app")
        global root
        #Define root window

        root = Tk()
        root.title('Coffee talk - Desktop application')
        root.geometry("400x400")
        #Root window features
        hello_label = Label(root, text="Welcome " + id_name)
        refreshButton = Button(root, text="Refresh", command = refresh)
        quitButton = Button(root, text="Sign out", command = self.signout)
        hello_label.pack()
        refreshButton.pack()
        quitButton.pack()



        #Main loop for tkinter
        root.mainloop()
        
    def display_login(self):
        print('display login')
        global root, myLabel, myButton
        global myTextbox
        #Define root window
        root = Tk()
        root.title('Coffee talk - Desktop application')
        root.geometry("400x100")
        #Root window features
        myLabel = Label(root, text="Enter name: ")
        myLabel.pack()
        myTextbox = Entry(root, width=30)
        myTextbox.pack()
        myButton = Button(root, text="Login", command= self.login)
        myButton.pack()

        #Main loop for tkinter
        root.mainloop()



    def display_callroom(self):
        #entry: display_welcome_msg, subscribe to mqtt
        #entry: display_callroom
        print('in callroom')


        #exit: unsubscribe mqtt
        return


    def login(self):
        print('in check id')
        global id_name
        id_name = myTextbox.get()
        if validate_ID(id_name):
            print('id valid')
            root.destroy()
            self.stm.send("valid")
            #loggedin()
            #videostream()
            #mqtt()
            #send to in_callroom
        else:
            print('id invalid')
            root.destroy()
            self.stm.send("invalid")
            messagebox.showerror("Error", "Login failed")
            return


    def signout(self):
        root.destroy()
        self.stm.send("logout")
    

    #idle()
    def print_message(self, tekst):
        print(tekst)

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

#de ulike statene
idle = {"name": "idle", "entry": "display_app"}
pre_login = {"name": "pre_login", "entry": "display_login"}
in_callroom = {"name": "in_callroom", "entry": "display_callroom"}




comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5], states=[idle, pre_login, in_callroom,], obj=comp, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()