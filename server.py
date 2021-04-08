import socket
from threading import Thread
import pickle
import os
import datetime

online_users = []


if os.path.exists("accounts.pickle") == False:
    with open('accounts.pickle', 'wb') as handle:
        pickle.dump([], handle, protocol=pickle.HIGHEST_PROTOCOL)

if os.path.exists("clique.pickle") == False:
    with open('clique.pickle', 'wb') as handle:
        pickle.dump([], handle, protocol=pickle.HIGHEST_PROTOCOL)


SERVER_HOST = "ip address"
SERVER_PORT = 5002
separator_token = "<SEP>"
client_sockets = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


def joinClique(msg):

    with open('accounts.pickle', 'rb') as handle:
        a = pickle.load(handle)

    for i in range(len(a)):
        if a[i]["username"] == msg.split("  ")[1]:
            #print(a[i]["username"], msg.split("  ")[0])
            a[i]["cliques"].append(msg.split("  ")[0])
            break
    handle.close()

    with open('accounts.pickle', 'wb') as handle:
        pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)

    handle.close()

def makeClique(msg, person):

    #Add the clique data
    
    with open('clique.pickle', 'rb') as handle:
        cliques = pickle.load(handle)

    handle.close()

    cliques.append(msg)

    with open('clique.pickle', 'wb') as handle:
        cliques = pickle.dump(cliques, handle, protocol=pickle.HIGHEST_PROTOCOL)

    handle.close()

    #Add the clique name to the users list of cliques

    with open('accounts.pickle', 'rb') as handle:
        accounts = pickle.load(handle)

    for i in range(len(accounts)):
        if accounts[i]["username"] == person:
            accounts[i]["cliques"].append(msg["name"])
            break
    handle.close()

    with open('accounts.pickle', 'wb') as handle:
        accounts = pickle.dump(accounts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    handle.close()

def sendText(msg):
    with open('clique.pickle', 'rb') as handle:
        c = pickle.load(handle)
    handle.close()

    for i in range(len(c)):
        if c[i]["name"] == msg.split("  ")[2]:
            c[i]["chat"] += msg.split("  ")[0] + msg.split("  ")[1] + "\n\n"
            online_members = c[i]["online_members"]
            break

    with open('clique.pickle', 'wb') as handle:
        pickle.dump(c, handle, protocol=pickle.HIGHEST_PROTOCOL)

    handle.close()

    msg = msg.split("  ")[0] + msg.split("  ")[1]

    for client_socket in online_members:
        client_socket.send(msg.encode())

def loginExists(msg, cs):
    #print(msg.split("  ")[2])

    with open('accounts.pickle', 'rb') as handle:
        a = pickle.load(handle)

    handle.close()

    username = msg.split("  ")[0]

    password = msg.split("  ")[1]

    for i in range(len(a)):

        if a[i]["username"] == username and a[i]["password"] == password:
            print(a[i]["cliques"])

            #Get whos online
            
            with open('clique.pickle', 'rb') as handle:
                b = pickle.load(handle)
            handle.close()

            for j in range(len(b)):
                if b[j]["name"] == msg.split("  ")[2]:
                    b[j]["online_members"].append(cs)

            with open('clique.pickle', 'wb') as handle:
                pickle.dump(b, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()

            #Return users cliques
            return a[i]["cliques"]
    return False

def makeAccount(msg, cs):

    with open('accounts.pickle', 'rb') as handle:
        accounts = pickle.load(handle)

    handle.close()
    #print(accounts)

    for i in range(len(accounts)):
        if accounts[i]["username"] == msg["username"]:
            cs.send("~$@srtmsg:signinfld".encode())
            return

    accounts.append(msg)
    
    with open('accounts.pickle', 'wb') as handle:
        pickle.dump(accounts, handle, protocol=pickle.HIGHEST_PROTOCOL)

    handle.close()

    #print(accounts)

def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    while True:

        try:
            msg = cs.recv(1024)
            try:
                msg = msg.decode()

                if "~$@srtmsg:login" in msg:
                    #See if login is valid
                    loginValid = loginExists(msg, cs)

                    if loginValid != False:
                        cliquesData = []
                        with open('clique.pickle', 'rb') as handle:
                            cliques = pickle.load(handle)

                        for i in range(len(cliques)):
                            #print(cliques[i])
                            if cliques[i]["name"] in loginValid:
                                cliquesData.append(cliques[i])

                        cs.send(pickle.dumps(cliquesData))
                        
                        #cs.send("~$@srtmsg:loginwrkd".encode())
                    else:
                        cs.send("~$@srtmsg:loginfled".encode())

                elif "~$@srtmsg:online" in msg:
                    username = msg.split("  ")[0]
                    online_users.append(username)
                    for client_socket in client_sockets:
                        client_socket.send(((' '.join(online_users)) + "  ~$@srtmsg:onlineusers").encode())

                elif "~$@srtmsg:joiningClique" in msg:
                    joinClique(msg)

                elif "~$@srtmsg:giveReqClique" in msg:
                    print("regclkiqwquuee!")
                    with open('clique.pickle', 'rb') as handle:
                        tempCliques = pickle.load(handle)
                    handle.close()
                    for i in range(len(tempCliques)):
                        if tempCliques[i]["name"] == msg.split("  ")[0]:
                            #print(tempCliques[i]["chat"])
                            cs.send((tempCliques[i]["chat"] + "  ~$@srtmsg:theReqsChat").encode())
                            break
                else:
                    #Means someone is just sending a text
                    print("sending text")
                    sendText(msg)

            except UnicodeDecodeError:
                msg = pickle.loads(msg)
                if msg["type"] == "user":
                    #User is creating account
                    makeAccount(msg, cs)
                elif msg["type"] == "clique":
                    print(msg)
                    makeClique(msg, online_users[client_sockets.index(cs)])

                
        except ConnectionResetError:
            #User left, should remove them
            print(online_users[client_sockets.index(cs)] + " has left the chat.")
            online_users.remove(online_users[client_sockets.index(cs)])
            client_sockets.remove(cs)

            for client_socket in client_sockets:
                client_socket.send(((' '.join(online_users)) + "  ~$@srtmsg:onlineusers").encode())
            return
            



while True:
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")
    client_sockets.append(client_socket)
    t = Thread(target=listen_for_client, args=(client_socket,))
    t.daemon = True
    t.start()

for cs in client_sockets:
    cs.close()

s.close()
