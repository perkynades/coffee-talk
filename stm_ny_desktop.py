#https://github.com/stigaro/ttm4115-project-team14


import os
#import paho.mqtt.client as mqtt
import logging
import json
import base64
import time
import sys
from appJar import gui
from stmpy import Driver, Machine
from threading import Thread, Lock
from uuid import uuid4



class DesktopApp:
    def __init__(self, transitions, states, debug):
        print("init")
        self.payload = {}
        self._logger = logging.getLogger(__name__)
        self._logger.info('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')
        self.debug = debug
        self.app = None

        #stm_walkie_talkie_name = "{}_walkie_talkie".format(self.name)
        desktop_machine = Machine(transitions=transitions, states=states, obj=self, name="stm_desktop")
        self.stm = desktop_machine

        #recognizer_stm = get_state_machine('stm_recognizer', [stm_walkie_talkie_name])

        self.stm_driver = Driver()
        self.stm_driver.add_machine(desktop_machine)
        #self.stm_driver.add_machine(recognizer_stm)
        self.stm_driver.start()
        self._logger.debug('Component initialization finished')


    def on_init(self):
        print("on init")
        # Create and start MQTT client on init
        #mqtt ting
        self._logger.debug('on_init started')
        # Create GUI in a new thread
        th = Thread(target=self.create_gui)
        th.start()
    

    def validate_ID(self, id_name):
        names = ["Emil", "Emilie", "Hanne", "Jonatan", "Sebastian"]
        if id_name in names:
            return True
        return False

    def login(self):
        print('in check id')
        global id_name
        id_name = self.app.getEntry("Login")
        if self.validate_ID(self, id_name):
            print('id valid')
            #self.stm.send("valid", "comp")
            self.stm.send("valid")
            print("id valid sent")
        else:
            print('id invalid')
            #self.stm.send("invalid", "comp")
            self.stm.send("invalid")
            print("id invalid sent")
            #self.app.errorBox("Failed login")
            #send to back to pre login
    
    def create_gui(self):
        self.app = gui()
        self.app.showSubWindow("en")
        #self.app.setStretch("both")
        #self.app.setSticky("")
        #self.app.setBgImage("images/bg.gif")

        if self.debug == True:
            self.app.setInPadding([30,40])
            self.app.setPadding([0,50])
        self.app.addLabel("title", "Coffee talk - Desktop", 0, 0)
        self.app.setLabelBg("title", "#3e3e3e")
        self.app.setLabelFg("title", "white")
        self.app.stopSubWindow()
        self.app.go()
        

    def login_gui(self):
        #self.app = gui()
        self.app.startSubWindow("to")
        print('display login')
        # add labels & entries
        # in the correct row & column
        self.app.addLabelEntry("Login")
        # start the GUI
        self.app.addButtons(["Submit"], self.login)
        #self.app.go()
        self.app.stopSubWindow()


    def desktop_gui(self):
        print("Display app")
        self.app.startSubWindow("tre")
        self.app.addLabel("title", "Coffee talk - Desktop")
        self.app.setLabelBg("title", "blue")
        self.app.addLabel("h1", "Here you can see the status of the rooms")
        self.app.addLabel("l1", "Coffee-room 1")
        self.app.addLabel("l2", "Coffee-room 2")
        self.app.addLabel("l3", "Lunch-room")
        self.app.addLabel("l4", "Private room")
        self.app.setLabelBg("l1", "red")
        self.app.setLabelBg("l2", "blue")
        self.app.setLabelBg("l3", "purple")
        self.app.setLabelBg("l4", "pink")
        self.app.setFont(12)
        self.app.addMessage("tekst_l1", "Participants Coffee-room 1")
        self.app.addMessage("tekst_l1_p", "No-one")
        self.app.addMessage("tekst_l2", "Participants Coffee-room 2")
        self.app.addMessage("tekst_l2_p", "No-one")
        self.app.addMessage("tekst_l3", "Participants Lunch-room")
        self.app.addMessage("tekst_l3_p", "No-one")
        self.app.addMessage("tekst_l4", "Participants Private room")
        self.app.addMessage("tekst_l4_p", "No-one")
        self.app.stopSubWindow()
        #self.app.go()

    def callroom_gui(self):
        self.app.startSubWindow("fire")
        #entry: display_welcome_msg, subscribe to mqtt
        #entry: display_callroom
        print('in callroom')
        #exit: unsubscribe mqtt
        self.app.stopSubWindow()
        #return


    def print_message(self, tekst):
        print(tekst)


t0 = {
    "source": "initial", 
    "target": "pre_login",
    "effect": "print_message('t0'); on_init"
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
idle = {"name": "idle", "entry": "desktop_gui"}
pre_login = {"name": "pre_login", "entry": "login_gui"}
in_callroom = {"name": "in_callroom", "entry": "callroom_gui"}

desktopApp=DesktopApp(transitions=[t0, t1, t2, t3, t4, t5], states=[idle, pre_login, in_callroom], debug=True)


#comp = DesktopApp()
#comp_machine = Machine(transitions=[t0, t1, t2, t3, t4, t5], states=[idle, pre_login, in_callroom], obj=comp, name="comp")
#comp.stm = comp_machine

#driver = Driver()
#driver.add_machine(comp_machine)

#driver.start()











































































#------------------------------------------------------------------------------------------------------------------------------
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_BASE = 'ttm4115/team_02/'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_14/command'

class MQTT_Client:
    def __init__(self, component):
        self.count = 0
        self.component = component
        # Callback methods
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("on_connect(): {}".format(mqtt.connack_string(rc)))
        self.component.stm.send("register")

    def on_message(self, client, userdata, msg):
        self.component._logger.debug("on_message(): topic: {}".format(msg.topic))
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            self.component.parse_message(payload)
        except Exception as err:
            self.component._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return

    def start(self, broker, port):
        print("Connecting to {}:{}".format(broker, port))
        self.client.connect(broker, port)
        try:
            thread = Thread(target=self.client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.client.disconnect()