from stmpy import Driver, Machine
from appJar import gui


def validate_ID(id_name):
    names = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
    if id_name in names:
        return True
    return False

#Signout function

    #pre_login

#Refresh function


class CompCommunication:

    #def __init__(self):
        
    

    def display_app(self):
        print("Display app")

        self.app.addLabel("title", "Coffee talk - Desktop")
        self.app.setLabelBg("title", "blue")

        self.app.startFrame("LEFT", row=0, column=0)        
        #self.app.setSticky("NEW")
        #self.app.setStretch("COLUMN")
        self.app.addLabel("h1", "Here you can see the status of the rooms")
        self.app.addLabel("l1", "Coffee-room 1")
        self.app.addLabel("l2", "Coffee-room 2")
        self.app.addLabel("l3", "Lunch-room")
        self.app.addLabel("l4", "Private room")
        self.app.setLabelBg("l1", "red")
        self.app.setLabelBg("l2", "blue")
        self.app.setLabelBg("l3", "purple")
        self.app.setLabelBg("l4", "pink")
        self.app.stopFrame()

        self.app.startFrame("RIGHT", row=0, column=1)        
        #self.app.setSticky("NEW")
        #self.app.setStretch("COLUMN")
        self.app.setFont(12)
        self.app.addMessage("tekst_l1", "Participants Coffee-room 1")
        self.app.addMessage("tekst_l1_p", "No-one")
        self.app.addMessage("tekst_l2", "Participants Coffee-room 2")
        self.app.addMessage("tekst_l2_p", "No-one")
        self.app.addMessage("tekst_l3", "Participants Lunch-room")
        self.app.addMessage("tekst_l3_p", "No-one")
        self.app.addMessage("tekst_l4", "Participants Private room")
        self.app.addMessage("tekst_l4_p", "No-one")
        self.app.stopFrame()
        self.app.go()




    def display_login(self):
        print('display login')
        self.app = gui()
        self.app.addLabel("title", "Coffee talk - Desktop")
        self.app.setLabelBg("title", "blue")
        # add labels & entries
        # in the correct row & column
        self.app.addLabelEntry("Login")
        self.app.addButtons(["Submit"], self.login)

        self.app.go()


    def display_callroom(self):
        
        print('in callroom')
        #entry: subscribe to mqtt

        #display_callroom
        callroom = "herskalvihentecallroom"
        self.app.addLabel("title", f'You are in {callroom}')
        self.app.setLabelBg("title", "blue")
        
        #exit: unsubscribe mqtt
        return
    

    
    def login(self):
        print('in check id')
        global id_name
        id_name = self.app.getEntry("Login")
        if validate_ID(id_name):
            print('id valid')
            #self.stm.send("valid", "comp")
            self.stm.send("valid")
            
            print("id valid sent")
            #loggedin()
            #videostream()
            #mqtt()
            #send to in_callroom
        else:
            print('id invalid')
            #self.stm.send("invalid", "comp")
            self.stm.send("invalid")
            self.app.errorBox("Failed login")
            #send to back to pre login
            return
            

    def print_message(self, tekst):
        print(tekst)

# initial transitions
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