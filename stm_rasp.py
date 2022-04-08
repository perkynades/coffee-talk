from stmpy import Driver, Machine
from tkinter import *


def validate_ID(id_name):
    names = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
    if id_name in names:
        return True
    return False

class RaspberryCommunication:
    def idle(self):
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
        myButton = Button(root, text="Login", command= login)
        myButton.pack()

        #Main loop for tkinter
        root.mainloop()
        # Just show website and start

    def in_callroom(self):
        #entry: join callroom, display_welcome_msg, send_to_mqtt
        #entry: display_callroom
        if validate_ID(id_name) and id_in_call and last_internal_participant:
            #           -> send_id_to_mqtt_leave, display_goodbye_msg
            #           -> return to idle state
            return

        elif validate_ID(id_name) and id_in_call:
            #           -> send_id_to_mqtt_leave, display_goodbye_msg
            return

        elif validate_ID(id_name) and id_not_in_call:
            #           -> send_id_to_mqtt_join, display_welcome_msg
            return
        elif validate_ID(id_name) and id_not_in_call:
            #           -> send_id_to_mqtt_join, display_welcome_msg
            return
        elif not validate_ID(id_name):
            return print('ID is invalid:((')
        #exit: leave_callroom

    #potensielt lage slik at den returnerer target state
    def check_ID(self):
        global id_name
        id_name = myTextbox.get()
        global wrong_label
        if validate_ID(id_name):
            loggedin()
            videostream()
            mqtt()
            #send to in_callroom
        else:
            wrong_label.pack()
            root.after(1000, lambda: wrong_label.destroy())
            #send to back to idle
            return



# initial transition
t0 = {
    "source": "initial", 
    "target": "idle"
}

t1 = {
    "trigger": "scan_id",
    "source": "idle",
    "target": "check_ID"
}

t2 = {
    "trigger": "id_invalid",
    "source": "check_ID",
    "target": "idle",
    "effect": "display_error"
}

t3 = {
    "trigger": "id_valid",
    "source": "check_ID",
    "target": "in_callroom",
    "effect": "display_welcome"
}

t4 = {
    "trigger": "end_participation",
    "source": "in_callroom",
    "target": "idle",
    "effect": "display_goodbye"
}

idle = {"name": "idle", "entry": "display_website"}
in_callroom = {"name": "in_callroom", "entry": "join_callroom, send_id_to_mqtt_join, display_callroom"}
check_ID = {"name": "check_ID", "entry": "id_valid"}




raspberry = RaspberryCommunication()
raspberry_machine = Machine(transitions=[t0, t1, t2, t3, t4], states=[idle, in_callroom, check_ID], obj=raspberry, name="raspberry")
raspberry.stm = raspberry_machine

driver = Driver()
driver.add_machine(raspberry_machine)

driver.start()
