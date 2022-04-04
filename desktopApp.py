from tkinter import *
from mqtt import MQTT_Client_1
from threading import Thread
import paho.mqtt.client as mqtt

#Define root window
root = Tk()
root.title('Coffee talk - Desktop application')
root.geometry("400x100")

#Valid users:
names = ["Emil", "Emilie", "Hanne", "Jonathan", "Sebastian"]

#Login function
def login():
    if myTextbox.get() in names:
        loggedin()
        mqtt()
    else:
        root.destroy()

def signout():
    root.destroy()

def loggedin():
    hello_label = Label(root, text="Welcome " + myTextbox.get())
    quitButton = Button(root, text="Sign out", command = signout)
    myLabel.destroy()
    myTextbox.destroy()
    myButton.destroy()
    hello_label.pack()
    quitButton.pack()

#MQTT function
def mqtt():
    print("MQTT")
    #broker, port = "mqtt.item.ntnu.no", 1883
    #client = MQTT_Client_1()
    #client.start(broker, port)


#Root window features
myLabel = Label(root, text="Enter name: ")
myLabel.pack()
myTextbox = Entry(root, width=30)
myTextbox.pack()
myButton = Button(root, text="Login", command= login)
myButton.pack()

#Main loop for tkinter
root.mainloop()