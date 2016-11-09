import socket               # Import socket module
import json
import threading
import time
import serial
def getJSON():
    fileLock.acquire()
    with open(filename,'r') as jsonFile:
        jsonData = json.load(jsonFile)
    fileLock.release()
    return jsonData

def putJSON(jsonData):
    fileLock.acquire()
    with open(filename,'w') as jsonFile:
        json.dump(jsonData,jsonFile,indent=4)
    fileLock.release()


class comArduino(threading.Thread):
    def __init__(self,tID,conn,op):
        threading.Thread.__init__(self)
        self.daemon = True
        self.threadID = tID
        self.serPort = conn
        self.operation = op
        self.strData = ""
    def run(self):
        if self.operation == 0:
            count = 0
            loop = 20
            l=1
            while count < loop:
                self.strData = makeResponse()
                readData(self.serPort,self.strData)
                count = count + 1
                time.sleep(1)
                l = l*-1
        elif self.operation == 1:
            writeData(self.serPort,self.strData)
    def putStr(self,request):
        self.strData = request

def writeData(conn,strRequest):
    portLock.acquire()
    print strRequest
    conn.flush()
    conn.write(strRequest)
    time.sleep(1)
    portLock.release()

def readData(conn,fixedStr):
    portLock.acquire()
    flag = True
    while flag:
        conn.flush()
        conn.write(fixedStr)
        time.sleep(1)
        resp = conn.read(4)
        if len(resp) == 4:
            flag = False
    jsonData = getJSON()
    jsonData['gate'] = ord(resp[0])
    jsonData['water']['level'] = ord(resp[1])
    jsonData['temp'][0] = ord(resp[2])
    jsonData['temp'][1] = ord(resp[3])
    putJSON(jsonData)
    print 'current states are',ord(resp[0]),ord(resp[1]),ord(resp[2]),ord(resp[3])
    portLock.release()

def waterControl(pumpState,level):
    signal = 0
    if pumpState == 1 and level == 10:
        signal = 0
    elif pumpState == 1 and level < 5:
        signal = 1
    return str(signal)

def tempControl(tempValue,threshold):
    kp = .2
    signal = kp*(int(tempValue) - int(threshold))
    if signal<0:
        signal = 0
    # print "setting temp bit",signal
    return str(signal)


def makeResponse():
    newSettings = bytearray("00000000000")
    jsonData = getJSON()
    newSettings[0] = str(jsonData['gate'])
    newSettings[1] = str(jsonData['lock'])
    newSettings[2] = waterControl(jsonData['water']['state'],jsonData['water']['level'])
    for light in jsonData['lights'] :
        if int(light['state']) == 1:
            newSettings[int(light['id'])+2] = str(light['value'])
    for appliance in jsonData['appliances']:
        if int(appliance['state']) == 1:
            newSettings[int(appliance['id'])+len(jsonData['lights'])+2] = tempControl(jsonData['temp'][appliance['id']-1],appliance['value'])
    return newSettings


filename = "home_states.json"
serialPort = serial.Serial('/dev/ttyACM1',115200,timeout = 1)

portLock = threading.Lock()
fileLock = threading.Lock()

readThread = comArduino(1,serialPort,0)
readThread.putStr(makeResponse())
readThread.start()

writeThread = comArduino(2,serialPort,1)

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
        fileLock.acquire()
        with open(filename,'r') as jsonFile:
            c.send(jsonFile.read())
        fileLock.release()

    elif requestLines[0] == 'SET STATS':
        keyValue = [message.split(": ") for message in requestLines[1:len(requestLines)-1]]
        if  keyValue[0][0] == "item":
            jsonData = getJSON()
            if keyValue[0][1] == "light" and keyValue[1][0] == "id" and keyValue[2][0] == 'state':
                loc = [i for i in range(len(jsonData['lights'])) if jsonData['lights'][i]['id'] == int(keyValue[1][1])]
                jsonData['lights'][loc[0]]['state'] = keyValue[2][1]
            elif keyValue[0][1] == "appliance" and keyValue[1][0] == "id" and keyValue[2][0] == 'state' and keyValue[3][0] == 'value':
                loc = [i for i in range(len(jsonData['appliances'])) if jsonData['appliances'][i]['id'] == int(keyValue[1][1])]
                jsonData['appliances'][loc[0]]['state'] = keyValue[2][1]
                if int(keyValue[3][1]) != -1:
                    jsonData['appliances'][loc[0]]['value'] = keyValue[3][1]
                writeThread.run()
            elif keyValue[0][1] == "mood" and keyValue[1][0] == 'state':
                intensity = '6'
                if keyValue[1][1] == 'default':
                    intensity = '4'
                elif keyValue[1][1] == 'movie':
                    intensity = '5'
                elif keyValue[1][1] == 'romantic':
                    intensity = '2'
                elif keyValue[1][1] == 'study':
                    intensity = '6'
                elif keyValue[1][1] == 'eco':
                    intensity = '3'
                elif keyValue[1][1] == 'sleep':
                    intensity = '1'
                jsonData['mood'] = keyValue[1][1]
                for light in jsonData['lights']:
                    light['value'] = intensity

            else:
                print "Error invalid request!"
            putJSON(jsonData)
            newSettings = makeResponse()
            writeThread.putStr(newSettings)
            readThread.putStr(newSettings)
            writeThread.run()
    else:
        c.send("Unknown request!");
    c.close()
    print "Connection closed with", addr
