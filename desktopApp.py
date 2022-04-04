from tkinter import *
from mqtt import MQTT_Client_1
from threading import Thread
import paho.mqtt.client as mqtt


#Login function
def login():
    #Valid users:
    names = ["Emil", "Emilie", "Hanne", "Jonathan", "Sebastian"]
    global wrong_label
    wrong_label = Label(root, text="Wrong login")
    if myTextbox.get() in names:
        loggedin()
        mqtt()
    else:
        wrong_label.pack()
        root.after(1000, lambda: wrong_label.destroy())
        root.after(1000)
        


#Signout function
def signout():
    root.destroy()
    idle()

#Refresh function
def refresh():
    print("refresh")

#Logged in state
def loggedin():
    hello_label = Label(root, text="Welcome " + myTextbox.get())
    refreshButton = Button(root, text="Refresh", command = refresh)
    quitButton = Button(root, text="Sign out", command = signout)
    myLabel.destroy()
    myTextbox.destroy()
    myButton.destroy()
    hello_label.pack()
    refreshButton.pack()
    quitButton.pack()
    

#MQTT function
def mqtt():
    print("MQTT")
    #broker, port = "mqtt.item.ntnu.no", 1883
    #client = MQTT_Client_1()
    #client.start(broker, port)

#Idle state
def idle():
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

idle()