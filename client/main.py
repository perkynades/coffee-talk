from stmpy import Driver, Machine

class Client:
    def __init__(self, transitions, states):
        self.app = None
        
        
        client_machine = Machine(transitions=transitions, states=states, obj=self, name="stm_desktop")
        self.stm = client_machine
        
        self.stm_driver = Driver()
        self.stm_driver.add_machine(client_machine)

        self.stm_driver.start()

    def on_login(self):
        print("Logging in")
        # Open website, log in
        # Make websockets report back when ok

# Transitions
t0 = {
    "source": "initial",
    "target": "join-callroom",
    "effect": "on_join_callroom"
}

t1 = {
    "trigger": "join_callroom",
    "source": "pre-login"
}

# States

idle = {"name": "idle", "entry": ""}