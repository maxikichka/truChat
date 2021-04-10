import socket
import random
from threading import Thread
from datetime import datetime
from tkinter import *
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import os
import pickle

online_users = []
version = "1.0"

def updated():
    url = "https://truchat-downloads.maxina.repl.co/"

    r = requests.get(url, allow_redirects=True)

    soup = BeautifulSoup(r.text, 'html.parser')

    link = soup.find(id="latestversion").get_text()

    if link == version:
        return True
    else:
        return False

def update():
    url = "https://truchat-downloads.maxina.repl.co/"

    r = requests.get(url, allow_redirects=True)

    soup = BeautifulSoup(r.text, 'html.parser')

    link = soup.find(id="latestversion").get("href")

    r = requests.get(link, allow_redirects=True)

    #print(r.text)


    open('client1.py', 'w').write(str(r.text))

    os.remove("client.py")

def getInClique():

    print(cliqueNameToJoin.get())

    s.send((cliqueNameToJoin.get() + "  " + userName + "  ~$@srtmsg:joiningClique").encode())

def joinAClique():
    global cliqueNameToJoin
    
    cliqueToJoin = Toplevel(win)

    cliqueNameToJoin = Entry(cliqueToJoin)
    cliqueNameToJoin.pack()

    join = Button(cliqueToJoin, text="Join", command=getInClique)

    join.pack()

    cliqueToJoin.mainloop()

def listen_for_messages():
    global message, online_users, userName, messageToReqs, messages
    
    while True:
        print("HI!!")

        message = s.recv(2048)

        try:
            message = message.decode()

            if "~$@srtmsg:loginfled" in message:

                messagebox.showerror("Login Failed", "Username or password is incorrect. ")

            elif "~$@srtmsg:signinfld" in message:
                messagebox.showerror("Signup Failed", "Username is taken. ")
            elif "~$@srtmsg:onlineusers" in message:
                online_users = message.split("  ")[0].split(" ")
                try:
                    online_label.config(text="Online:\n" + ', '.join(online_users))
                except NameError:
                    pass

            elif "~$@srtmsg:theReqsChat" in message:
                messageToReqs = message.split("  ")[0]

                messages = Text(win)

                messages.insert(END, messageToReqs)

                messages.grid(row=1, column=1)

            elif "~$@srtmsg:cliqueNotAvail" in message:
                messagebox.showerror("Clique Not Available", "You can not join this clique either because you are already in it or it does not exist. ")

            elif "~$@srtmsg:cliqueIsAvail" in message:
                cliquesList.insert(END, cliqueNameToJoin.get())

            else:
                messages.insert(END, message + "\n\n")

        except UnicodeDecodeError:
            #login worked
            #online_users.append(userName)
            #s.send((userName + "  ~$@srtmsg:online").encode())

            homePage(pickle.loads(message))

def createClique():
    cliquesList.insert(END, cliqueName.get())

    s.send(pickle.dumps({"type": "clique", "name": cliqueName.get(), "description": cliqueDescription.get("1.0", END), "chat": "", "members": [], "online_members": []}))

    makeNewClique.destroy()

    return

def newClique():

    global cliqueName, cliqueDescription, makeNewClique
    
    makeNewClique = Toplevel(win)

    makeNewClique.configure(bg="black")


    cliqueName = Entry(makeNewClique)

    cliqueName.pack()


    cliqueDescription = Text(makeNewClique)

    cliqueDescription.pack()


    finish = Button(makeNewClique, text="Create Clique", command=createClique)

    finish.pack()

    makeNewClique.mainloop()

def sendData():
    #while True:
    #typeArea.delete(0, END)
    #s.send(message.encode())     
    #break 
    return

def sendDataThread(*args):

    #global message

    message = (userName + ":  " + typeArea.get() + "  " + selectedClique)

    #messages.insert(END, userName + ":  " + typeArea.get() + "\n\n")


    typeArea.delete(0, END)
    s.send(message.encode())


    #snd = Thread(target = sendData)
    #snd.daemon = True
    #snd.start()

def chatApp(*args):
    global typeArea, messages, win, online_label, selectedClique

    selectedClique = cliquesList.get(cliquesList.curselection()[0])


    s.send((selectedClique + "  ~$@srtmsg:giveReqClique").encode())

    s.send((userName + "  ~$@srtmsg:online").encode())

    try:
        messages.destroy()
        typeArea.destroy()
        online_label.destroy()
        send.destroy()

    except NameError:
        pass

    typeArea = Entry(win, width=100)

    typeArea.bind("<Key>")

    typeArea.bind("<Return>", sendDataThread)

    typeArea.grid(row=2, column=1)

    online_label = Label(win, text="Online:\n" + ', '.join(online_users))
    online_label.grid(row=3, column=1)


    send = Button(win, text=">", command=sendDataThread)

    send.grid(row=2, column=2)

def homePage(cliques):
    global cliquesList

    print(cliques)

    loginWin.destroy()
    logIn.destroy()
    signup.destroy()
    updateApp.destroy()

    cliquesList = Listbox(win)

    for i in range(len(cliques)):
        cliquesList.insert(i + 1, cliques[i])

    cliquesList.bind("<<ListboxSelect>>", chatApp)

    cliquesList.grid(row = 0, column = 0)

    addClique = Button(win, text="Add a clique", command=newClique)

    addClique.grid(row = 1, column = 0)

    joinClique = Button(win, text="Join a Clique", command=joinAClique)

    joinClique.grid(row = 2, column = 0)

    #chatApp()

def checkIfExists():
    global userName

    userName = name.get()

    message = name.get() + "  " + passWord.get() + "  ~$@srtmsg:login"

    passWord.get()

    s.send(message.encode())

def logInAcc():
    global name, passWord, loginWin
    
    loginWin = Toplevel(win)

    name = Entry(loginWin)

    name.pack()


    passWord = Entry(loginWin)

    passWord.pack()

    start = Button(loginWin, text="Login", command=checkIfExists)

    start.pack()


    loginWin.mainloop()

def makeAccount():

    #message = username.get() + "  " + password.get() + "  ~$@srtmsg:signup"

    userData = {"type": "user", "username": username.get(), "password": password.get(), "cliques": []}

    message = pickle.dumps(userData)

    s.send(message)
    print(message)


    login.destroy()


def signUp():
    global username, password, login
    login = Toplevel(win)

    username = Entry(login)

    username.pack()


    password = Entry(login)

    password.pack()

    makeaccount = Button(login, text="Signup", command = makeAccount)

    makeaccount.pack()


    login.mainloop()

SERVER_HOST = "192.168.0.231"
SERVER_PORT = 5002
separator_token = "<SEP>"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")


snd = Thread(target = listen_for_messages)

snd.daemon = True

snd.start()


win = Tk()

win.geometry("800x800")

win.configure(bg="Black")

logIn = Button(win, text="Sign in", command=logInAcc)

logIn.pack()

signup = Button(win, text="Sign up", command=signUp)

signup.pack()

if updated():

    updateApp = Button(win, text="All up to date!", command=update)

    updateApp.pack()
else:
    updateApp = Button(win, text="Newer version avilable\n(Update Now)", command=update)

    updateApp.pack()


win.mainloop()



s.close()
