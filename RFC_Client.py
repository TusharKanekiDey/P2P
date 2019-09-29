import pprint
import ast
import os
import socket
import pickle
import csv
import sys

server, BUFFER_SIZE = '127.0.0.1',2048
print('enter your hostname')
host=input()
farg=sys.argv[0]
loc = os.path.dirname(farg)+'\\RFC_Files\\'+host

class Peer:
    def __init__(self,host,port,cookie):
        self.host=host
        self.port=port
        self.cookie=cookie

class PeerNode():
    def __init__(self, peer):
        self.peer_obj = peer
        self.next = None


class Peerlist():
    def __init__(self):
        self.head = None

    def add(self, peer_obj):
        node = PeerNode(peer_obj)
        node.next = self.head
        self.head = node

    def delete(self, host):
        tmp = self.head
        prev = None
        found = False

        while found == False:
            p_obj = tmp.peer_obj
            if p_obj.host == host:
                found = True
            else:
                prev = tmp
                tmp = tmp.next

            if prev == None:
                self.head = tmp.next
            else:
                prev.next = tmp.next
                
def isPresent(plist, host):
    tmp = plist.head
    while (tmp != None):
        p_obj = tmp.peer_obj
        if p_obj.host == host:
            return True
        tmp = tmp.next
    return False



class RSPeer:
    def __init__(self,host,port):
        self.host = host
        self.port = port

class RFCNode():
    def __init__(self, rfc):
        self.rfc_obj = rfc
        self.next = None


class RFClist():
    def __init__(self):
        self.head = None

    def add(self, rfc_obj):
        node = RFCNode(rfc_obj)
        node.next = self.head
        self.head = node

    def delete(self, host):
        tmp = self.head
        prev = None
        found = False

        while found == False:
            rf_obj = tmp.rfc_obj
            if rf_obj.host == host:
                found = True
            else:
                prev = tmp
                tmp = tmp.next

            if prev == None:
                self.head = tmp.next
            else:
                prev.next = tmp.next

    def write_csv(self):
        dup = check_dup(self, loc)
        tmp = self.head

        with open(loc + '\\index_list.csv', 'a') as f:
            while (tmp != None):
                index = tmp.rfc_obj
                if (len(dup) == 0):
                    row = index.rfc_no + ',' + index.title + ',' + index.hostname + '\n'
                    f.write(row)
                else:
                    if (index.hostname in dup):
                        print('Entry found')
                    else:
                        row = index.rfc_no + ',' + index.title + ',' + index.hostname + '\n'
                        f.write(row)

                tmp = tmp.getNext()
        f.close()




def main():
    print('Enter which server you want to connect to ? 1. RSServer 2.RFCServer of another Peer')
    type = input()
    objectRecv = Peerlist()
    newObjectRecv = RFClist()
    client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverPort = int(sys.argv[1])
    #serverPort = 4434
    mf = 'utf-8'

    if(type==1):
        print('Enter the communication type 1.Register 2.PQuery 3.Leave 4.KeepAlive')
        messageType = input()
        HOST='localhost'
        PORT=65500

        client_connect.connect((HOST, PORT))
        f_name = hostname + 'Cookie.txt'  # Cookie information is being maintained in a file
        try:
            file = open(f_name, 'r')
            peerInfo = ast.literal_eval(file.read())
            file.close()
            cookie = peerInfo.get('cookie', 'None')
        except IOError:
            if messageType == "Register":
                cookie = 'None'
                sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nPort ' + str(
                        serverPort) + ' <cr> <lf>\nCookie ' + str(cookie) + ' <cr> <lf>\nOperating System ' + str(
                        platform.platform()) + ' <cr> <lf>\n'
                print(sendMessage)
                client_connect.send(sendMessage.encode(mf))
                try:  # The peer receives its cookie information only if it's registering for the first time.
                    P0 = Peer(hostname, serverPort)
                    recvMessage = (client_connect.recv(BUFFER_SIZE).decode('utf-8'))
                    print('From Server\n', recvMessage)
                    P0.cookie = int(
                        recvMessage[recvMessage.index('cookie') + 6:recvMessage.index('<cr> <lf>\nFrom')])
                    print('Cookie information updated: Cookie is ', P0.cookie)
                    print('Saving cookie in ' + hostname + 'Cookie.txt')
                    attributes = vars(P0)
                    f_name = hostname + 'Cookie.txt'
                    file = open(f_name, 'w')
                    file.write(pprint.pformat(attributes))
                    file.close()
                except:
                    print('Already Registered and active')
                    client_connect.close()

            if messageType == 'PQuery':
                sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nserverPort ' + str(
                    serverPort) + ' <cr> <lf>\nCookie ' + str(cookie) + ' <cr> <lf>\nOperating System ' + str(
                    platform.platform()) + ' <cr> <lf>\n'
                print(sendMessage)
                client_connect.send(sendMessage.encode(mf))
                recvMessage = (client_connect.recv(BUFFER_SIZE).decode(mf))
                print('From Server\n', recvMessage)
                try:  # The RS Server sends the list of active peers only if the requesting peer is currently active and has already registered.
                    l_file = client_connect.makefile(mode='rb')
                    objectRecv = pickle.load(l_file)
                    l_file.close()
                    if (objectRecv.head == None):
                        print('No Other peers are active')
                    else:
                        print('List of active peers\n')
                        movnode = objectRecv.head
                        if (movnode!= None):
                            detail=movnode.peer_obj
                            print(detail.hostname, detail.port)
                        while(movnode.next!= None):
                            movnode=movnode.next()
                            detail = movnode.peer_obj
                            print(detail.hostname, detail.port)
                except:
                    print('Peer not registered or left. Register to get PeerList')
                    client_connect.close()

            if messageType == 'Leave':
                sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nPort ' + str(
                    serverPort) + ' <cr> <lf>\nCookie ' + str(cookie) + ' <cr> <lf>\nOperating System ' + str(
                    platform.platform()) + ' <cr> <lf>\n'
                print(sendMessage)
                client_connect.send(sendMessage.encode(mf))
                try:
                    recvMessage = (client_connect.recv(BUFFER_SIZE).decode(mf))
                    print('From Server\n', recvMessage)
                    client_connect.close()
                except:
                    print('Peer already left')

            if messageType == 'KeepAlive':
                sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nPort ' + str(
                    serverPort) + ' <cr> <lf>\nCookie ' + str(cookie) + ' <cr> <lf>\nOperating System ' + str(
                    platform.platform()) + ' <cr> <lf>\n'
                print(sendMessage)
                client_connect.send(sendMessage.encode(mf))
                recvMessage = client_connect.recv(BUFFER_SIZE).decode(mf)
                print('From Server\n', recvMessage)
                client_connect.close()

    elif (type == '2'):  # If the client peer wants to connect to an RFC server
        print('Connecting to RFCServer:', serverPort)
        clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSock.connect((serverHost, serverPort))
        print('Enter your hostname')
        print('Enter the type of action: 1.RFCQuery  2.GetRFC')
        messageType = input()
        if messageType == 'RFCQuery':
            keep_Alive = False
            sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>\nKEEP_ALIVE ' + str(keep_Alive)
            print(sendMessage)
            clientSock.send(sendMessage.encode(mf))
            recvMessage = clientSock.recv(BUFFER_SIZE).decode(mf)
            print('From Server\n', recvMessage)
            if ('RFCQuery Found' in recvMessage):
                file = clientSock.makefile(mode='rb')
                objectRecv1 = pickle.load(file)
                print('RFC Index sent by the server\n')
                movnode = objectRecv1.head
                if (movnode != None):
                    detail = movnode.rfc_obj
                    print(detail.rfc_no, ',', detail.title, ',', detail.hostname)
                while (movnode.next != None):
                    movnode = movnode.next()
                    detail = movnode.rfc_obj
                    print(detail.rfc_no, ',', detail.title, ',', detail.hostname)
                file.close()
                objectRecv1.write_csv()

        if messageType == 'GetRFC':
            print('enter rfc number to download')
            rfc_no = input()
            keep_Alive = False
            sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + hostname + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>RFC_NO ' + rfc_no + ' <cr> <lf>\nKEEP_ALIVE ' + str(keep_Alive)
            print(sendMessage)
            clientSock.send(sendMessage.encode('utf-8'))
            filename = 'rfc' + rfc_no + '.txt'
            f = open(loc + '\\' + filename, 'wb')
            recvMessage = clientSock.recv(BUFFER_SIZE).decode('utf-8')
            print('From Server\n', recvMessage)
            fileSize = int(recvMessage[recvMessage.index('Content Length ') + 15:])
            while (fileSize > 0):
                print('receiving data...')
                data = clientSock.recv(BUFFER_SIZE)
                print('data=%s', data)
                f.write(data)
                fileSize = fileSize - BUFFER_SIZE
            f.close()
            print('Successfully got the file')
        clientSock.close()
                    







if __name__ == "__main__":
    main()
