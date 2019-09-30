import pprint
import ast
import os
import socket
import pickle
import csv
import sys
import platform

server, BUFFER_SIZE = '127.0.0.1',2048
print('enter your hostname')
host=input()
farg=sys.argv[0]
loc = os.path.dirname(farg)+'\\RFC_Files\\'+host

class Peer:
    def __init__(self,host,port,cookie=None):
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

def check_dup(objectRecv,loc):
	list1=[]
	list2=[]
	dup=[]
	with open(loc+'\\index_list.csv','r') as f:
		reader=csv.reader(f)
		for row in reader:
			list1.append(row[2])

	f.close()
	tmp=objectRecv.head
	while(tmp!=None):
		index=tmp.getNode()
		list2.append(index.hostname)
		tmp=tmp.getNext()

	set1=set(list1)
	set2=set(list2)
	for p in list(set1):
		for i in range(len(list(set2))):
			if(p==list(set2)[i]):
				dup.append(p)
	return dup


def main():
    print('Enter which server you want to connect to ? 1. RSServer 2.RFCServer of another Peer')
    type = int(input())
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

        client_connect.connect((HOST, PORT))  #connecting to RS Server

        f_name = host + 'Cookie.txt'  # Cookie information is being maintained in a file
        try:
            with open(f_name) as f:
                content = f.readlines()
            send_cookie = content[0]

        except IOError:
            send_cookie = None

        global_cookie = send_cookie

        if messageType == "Register":
                
            sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nPort ' + str(
                    serverPort) + ' <cr> <lf>\nCookie ' + str(send_cookie) + ' <cr> <lf>\nOperating System ' + str(
                    platform.platform()) + ' <cr> <lf>\n'
            print(sendMessage)
            client_connect.send(sendMessage.encode('utf-8'))
            #try:  # The peer receives its cookie information only if it's registering for the first time.
        
            recvMessage = (client_connect.recv(BUFFER_SIZE).decode('utf-8'))
            print('From Server\n', recvMessage)
            recv_cookie = int(
                recvMessage[recvMessage.index('cookie') + 6:recvMessage.index('<cr> <lf>\nFrom')])
            if 'Already' in recvMessage:
                print('Already Registered')
                global_cookie = recv_cookie
                client_connect.close()
            else:
                print('Cookie information updated: Cookie is ', recv_cookie)
                print('Saving cookie in ' + host + 'Cookie.txt')

                global_cookie = recv_cookie                
                f_name = host + 'Cookie.txt'
                file = open(f_name, 'w')
                file.write(str(recv_cookie))
                file.close()
            #except:
                #print('Already Registered and active')
                #global_cookie = send_cookie
                #client_connect.close()
###############################################################################################

        if messageType == 'PQuery':

            sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nserverPort ' + str(
                serverPort) + ' <cr> <lf>\nCookie ' + str(global_cookie) + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>\n'
            print(sendMessage)
            client_connect.send(sendMessage.encode(mf))
            recvMessage = (client_connect.recv(BUFFER_SIZE).decode('utf-8'))
            print('From Server\n', recvMessage)
            #try:  # The RS Server sends the list of active peers only if the requesting peer is currently active and has already registered.
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
                    print(detail.host, detail.port)
                while(movnode.next!= None):
                    movnode=movnode.next
                    detail = movnode.peer_obj
                    print(detail.host, detail.port)
            #except:
            #print('Peer not registered or left. Register to get PeerList')
            client_connect.close()
 ##########################################################################################################

        if messageType == 'Leave':
            sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nPort ' + str(
                 serverPort) + ' <cr> <lf>\nCookie ' + str(global_cookie) + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>\n'
            print(sendMessage)
            client_connect.send(sendMessage.encode('utf-8'))
            try:
                recvMessage = (client_connect.recv(BUFFER_SIZE).decode('utf-8'))
                print('From Server\n', recvMessage)
                client_connect.close()
            except:
                print('Peer already left')

        if messageType == 'KeepAlive':
            sendMessage = 'POST ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nPort ' + str(
                serverPort) + ' <cr> <lf>\nCookie ' + str(global_cookie) + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>\n'
            print(sendMessage)
            client_connect.send(sendMessage.encode('utf-8'))
            recvMessage = client_connect.recv(BUFFER_SIZE).decode('utf-8')
            print('From Server\n', recvMessage)
            client_connect.close()










if __name__ == "__main__":
    main()