import socket               # Import socket module
import json
import threading
import time

class comArduino(threading.Thread):
    def __init__(self,tID,conn,op):
        threading.Thread.__init__(self)
        self.threadID = tID
        self.serPort = conn
        self.operation = op
    def run(self):
        threadLock.acquire()
        if self.operation==0:
            readData(self.serPort)
        elif self.operation==1:
            pass
            # writeData()
        threadLock.release()


def readData(conn):
    count = 0
    count = count+1
    # while flag:
    #     conn.flush()
    #     conn.write(b'012345')
    #     resp = conn.read(4)
    #     if (len(resp) == 4):
    #         flag = False
    # with open(filename,'r') as jsonFile:
    #     jsonData = json.load(jsonFile)
    #     jsonData['gate'] = ord(resp[0])
    #     jsonData['water']['level'] = ord(resp[1])
    #     jsonData['temp'][0] = ord(resp[2])
    #     jsonData['temp'][1] = ord(resp[2])
    # with open(filename,'w') as jsonFile:
    #     jsonFile.write(json.dump(jsonData))
    print 'reading from arduino'
    time.sleep(1)

filename = "home_states.json"
threadLock = threading.Lock()
thread1 = comArduino(1,2,0)
thread1.start()
count = 0
while count<10:
    thread1.run()
    time.sleep(1)
    count = count + 1

sock = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 5000                # Reserve a port for your service.
print "Server starting...."
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", port))        # Bind to the port
sock.listen(5)                 # Now wait for client connection.
print "Server started!"

while True:
    c, addr = sock.accept()     # Establish connection with client.
    print 'Connected to ', addr

    request =  c.recv(2048)
    requestLines = request.split("\n");
    print requestLines

    if requestLines[0] == 'GET STATS':
        with open(filename,'r') as jsonFile:
            c.send(jsonFile.read())

    elif requestLines[0] == 'SET STATS':
        keyValue = [message.split(": ") for message in requestLines[1:len(requestLines)-1]]
        if  keyValue[0][0] == "item":
            with open(filename,'r') as jsonFile:
                jsonData = json.load(jsonFile)
                print keyValue[1][1]
            if keyValue[0][1] == "light" and keyValue[1][0] == "id" and keyValue[2][0] == 'state':
                loc = [i for i in range(len(jsonData['lights'])) if jsonData['lights'][i]['id'] == int(keyValue[1][1])]
                jsonData['lights'][loc[0]]['state'] = keyValue[2][1]
            elif keyValue[0][1] == "appliance" and keyValue[1][0] == "id" and keyValue[2][0] == 'state':
                loc = [i for i in range(len(jsonData['lights'])) if jsonData['lights'][i]['id'] == int(keyValue[1][1])]
                jsonData['lights'][loc[0]]['state'] = keyValue[2][1]
            elif keyValue[0][1] == "mood" and keyValue[1][0] == 'state':
                jsonData['mood'] = keyValue[1][1]
            else:
                print "Error invalid request!"
            with open(filename,'w') as jsonFile:
                json.dump(jsonData,jsonFile,indent=4)
    else:
        c.send("Unknown request!");
    c.close()
    print "Connection closed with", addr
