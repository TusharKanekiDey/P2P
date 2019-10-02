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
loc = os.path.dirname(farg) +host+'/RFC_Files'
print(loc)
#RFC_reqd = [4,5,6,7]
#RFC_reqd_set = set(RFC_reqd)


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
                




class RFCIndex:
    def __init__(self,rfc_no,tile,hname):
        self.rfc_no = rfc_no
        self.title = title
        self.hostname = hname

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


    def merge_RFC(self):
        dup = self.get_duplicate(loc)
        tmp = self.head

        with open(loc + '/index_list.csv', 'a') as f:
            while (tmp != None):
                index = tmp.rfc_obj
                if (index.rfc_no not in dup):
                    row = '\n'+index.rfc_no + ',' + index.title + ',' + index.hostname 
                    f.write(row)
                else:
                    print('RFC already found')
                tmp = tmp.next
        f.close()

    def get_duplicate(self,loc):
        list1=set()
        dup=set()

        with open(loc+'/index_list.csv','r') as f:
            reader=csv.reader(f)
            for row in reader:
                #print(row)
                if len(row) != 0:
                    list1.add(row[0])

        f.close()
        tmp=self.head
        while(tmp!=None):
            r_obj=tmp.rfc_obj
            if r_obj.rfc_no  in list1:
                dup.add(r_obj.rfc_no)
            tmp=tmp.next
        return dup


def main():
    print('Enter which server you want to connect to ? 1. RSServer 2.RFCServer of another Peer')
    type = int(input())
    objectRecv = Peerlist()
    RFC_recv = RFClist()
    client_connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverPort = int(sys.argv[1])
    
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


        if messageType == 'PQuery':

            sendMessage = 'GET ' + messageType + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nserverPort ' + str(
                serverPort) + ' <cr> <lf>\nCookie ' + str(global_cookie) + ' <cr> <lf>\nOperating System ' + str(
                platform.platform()) + ' <cr> <lf>\n'
            print(sendMessage)
            client_connect.send(sendMessage.encode(mf))
            recvMessage = (client_connect.recv(BUFFER_SIZE).decode('utf-8'))
            print('From Server\n', recvMessage)
            #try:  # The RS Server sends the list of active peers only if the requesting peer is currently active and has already registered.
            #l_file = client_connect.makefile(mode='rb')
            #objectRecv = pickle.load(l_file) 
            #l_file.close()
            data =''
            flag_ch =0
            while True:
                recv_msg = client_connect.recv(BUFFER_SIZE)
                recv_msg = recv_msg.decode('utf-8')
                if recv_msg == 'emptylist':
                    flag_ch=1
                    break
                data += recv_msg
                if len(recv_msg) < BUFFER_SIZE:
                    break

            if flag_ch !=1: #checking data is empty or not
            
                data = data.split('*')
                for dat in data:
                    if len(dat) >0:
                        slist = dat.split(",")
                        if len(slist) > 0:
                            n_pobject = Peer(slist[0],slist[1])
                            objectRecv.add(n_pobject)
                    

                if (objectRecv.head == None):
                    print('No Other peers are active')
                else:
                    print('List of active peers\n')
                    #writing active peers to file
                    if os.path.exists(loc+'/'+'active.csv'):
                        os.remove(loc+'/'+'active.csv')
                    active_f = open(loc+'/'+'active.csv','w+')


                    movnode = objectRecv.head
                    if (movnode!= None):
                        detail=movnode.peer_obj
                        print(detail.host, detail.port)
                        active_f.write(detail.host+','+detail.port+'\n')
                    while(movnode.next!= None):
                        movnode=movnode.next
                        detail = movnode.peer_obj
                        print(detail.host, detail.port)
                        active_f.write(detail.host+','+detail.port+'\n')
                    active_f.close()
            else:
                print('No other peers are active')
            client_connect.close()
 

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
        ######################################################################################################################################
        #end of RS Server communication

    elif type==2:
        flag = 0
        RFC_reqd_set = set()
        print('Enter the number of RFCs you want to download:')
        no_RFC = int(input())
        while no_RFC != 0:
            print('Enter the RFC number you want to download:')
            numb = input()
            RFC_reqd_set.add(numb)
            no_RFC = no_RFC -1
        
        with open(loc+'/active.csv','r') as act_f:
            active_reader = csv.reader(act_f)
            for active_row in active_reader:
                serverport = int(active_row[1])
                print(serverport)
            #tmp = objectRecv.head #active peerlist head
            #while(tmp!=None):
                print('entered the loop')
                #p_obj = tmp.peer_obj
                #serverport = p_obj.port
                clientSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                clientSock.connect((server,serverport))

                #RFC Query
                send_msg = 'GET RFC Query'  + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nOperating System '+ str(platform.platform()) 
                print(send_msg)
                clientSock.send(send_msg.encode('utf-8'))

                recv_msg =  clientSock.recv(BUFFER_SIZE).decode('utf-8') 
                print('From Server:\n',recv_msg)

                if 'RFCQuery Found' in  recv_msg:
                    file=clientSock.makefile(mode='rb')
                    RFC_recv = pickle.load(file)

                    file.close()
                    RFC_recv.merge_RFC()
                else:
                    print('RFC Query not found. Check in the location')
                
                #send server the number of RFC's it has that it will download
                rfc_it_has =0
                with open(loc+'/index_list.csv','r') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if len(row) != 0 and row[0] in RFC_reqd_set:
                            rfc_it_has = rfc_it_has +1
                f.close()

                send_msg = 'GET Check ' + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>\n Number ' + str(rfc_it_has) + ' <cr> <lf>NN\n'
                print(send_msg)
                clientSock.send(send_msg.encode('utf-8'))


                
                with open(loc+'/index_list.csv','r') as f:
                    reader=csv.reader(f)
                    for row in reader:
                        if len(RFC_reqd_set) == 0:
                            flag =1
                            break

                        #cum_time_list =[]
                        #cum_time = 0
                        if len(row)!= 0 and row[0] in RFC_reqd_set:
                            #start_time = time.time()
                            send_msg = 'GET GetRFC ' + ' P2P/DI-1.1 <cr> <lf>\nHost ' + host + ' <cr> <lf>\nOperating System '+ str(platform.platform()) +' <cr> <lf>RFC_NO ' + row[0] + ' <cr> <lf>NN\n'
                            clientSock.send(send_msg.encode('utf-8'))
                            filename = 'rfc'+row[0]+'.txt'
                            ff = open(loc+'/'+filename, 'wb')
                            recv_msg = clientSock.recv(BUFFER_SIZE).decode('utf-8')
                            print('Server sent message\n', recv_msg)
                            fsize = int(recv_msg[recv_msg.index('Content Length ')+15:])
                            while fsize > 0:
                                print('..... data transfer....\n')
                                data = clientSock.recv(BUFFER_SIZE)
                                ff.write(data)
                                fsize = fsize - BUFFER_SIZE
                            ff.close()
                            print("Succesful file transfer\n")
                            RFC_reqd_set.remove(row[0]) #removing RFC's transferred
                            #end_time = time.time()
                        #cum_time+= end_time - start_time
                        #cum_time_list.append(cum_time)

                f.close()
                clientSock.close()
                if flag ==1:
                    break

            #tmp = tmp.next #go to next active peer list
            act_f.close()



            



















if __name__ == "__main__":
    main()