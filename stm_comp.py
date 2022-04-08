from stmpy import Driver, Machine

class CompCommunication:
    def idle(self):
        print("display callrooms and participants")
        # Just show website and start
        #refresh?

    def pre_login(self):
        print("display login screen")
        #just show login    

    def in_callroom(self):
        #entry: display_welcome_msg, subscribe to mqtt
        #entry: display_callroom

        #exit: unsubscribe mqtt
        return

    
    def check_ID(self):
        if id_valid:
            #send to in_callroom
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
    "effect": "display_error"
}

t3 = {
    "trigger": "id_valid",
    "source": "check_ID",
    "target": "idle",
    "effect": "display_welcome"
}

t4 = {
    "trigger": "join_callroom",
    "source": "idle",
    "target": "in_callroom",
    "effect": "display_call"
}

t5 = {
    "trigger": "leave_callroom",
    "source": "in_callroom",
    "target": "idle",
    "effect": "display_goodbye"
}

t5 = {
    "trigger": "logout",
    "source": "idle",
    "target": "pre_login",
    "effect": "display_logout"
}

idle = {"name": "idle", "entry": "display_website"}
in_callroom = {"name": "in_callroom", "entry": "subscribe_mqtt, display_callroom"}
check_ID = {"name": "check_ID", "entry": "id_valid"}




comp = CompCommunication()
comp_machine = Machine(transitions=[t0, t1, t2, t3, t4], states=[idle, in_callroom, check_ID], obj=raspberry, name="comp")
comp.stm = comp_machine

driver = Driver()
driver.add_machine(comp_machine)

driver.start()
