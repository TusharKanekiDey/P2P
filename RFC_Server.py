import socket
import threading
import csv
import time
import pickle
import sys,os
from threading import Thread
from socketserver import ThreadingMixIn
from datetime import datetime
import platform

Host = ''
port = int(sys.argv[1])
print('enter your hostname:')
host=input()

BUFFER_SIZE=2048
TTL_TIME=30
farg=sys.argv[0]
loc = os.path.dirname(farg) +host+'/RFC_Files'

class RFCIndex:
    def __init__(self,rfc_no,title,hname):
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

class peerThread(threading.Thread):
    def __init__(self,socket,clientIP):
        threading.Thread.__init__(self)
        self.lock=threading.Lock()
        print(self.lock)
        self.csocket=socket
        self.ip=clientIP[0]
        self.socket=clientIP[1]

    def run(self):
        print("Connection request from:" + threading.currentThread().getName())
        get_msg = self.csocket.recv(BUFFER_SIZE).decode('utf-8')

        if 'RFC Query' in  get_msg:
            RFC_list = RFClist()
            with open(loc+'/index_list.csv','r') as f:
                reader=csv.reader(f)
                for row in reader:
                    rfc_object = RFCIndex(row[0],row[1],row[2])
                    RFC_list.add(rfc_object)
            
            f.close()

            tmp_object = RFC_list.head
            if tmp_object != None:
                send_msg = 'POST RFCQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                print(send_msg)
                self.csocket.send(send_msg.encode('utf-8'))
                self.lock.acquire()
                self.csocket.send(pickle.dumps(RFC_list,pickle.HIGHEST_PROTOCOL))
                self.lock.release()
            
            else:
                send_msg = 'POST RFCQuery Not Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))
                print(send_msg)
        
        get_msg = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
        print(get_msg)
        loop_no=0
        if 'Check' in get_msg:
            loop_no= int(get_msg[get_msg.index('Number')+6:get_msg.index(' <cr> <lf>NN\n')].strip())
        
        while loop_no !=0:
            get_msg = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
            rfc_no= get_msg[get_msg.index('RFC_NO ')+7:get_msg.index(' <cr> <lf>NN\n')]
            fname = 'rfc'+rfc_no+'.txt'
            try:
                f = open(loc+'/'+fname,'rb')
                fsize = os.stat(loc +'/'+fname).st_size
                #print("fsize is ",fsize)
                send_msg = 'POST RFC Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) + '<cr> <lf>\nContent Length ' + str(fsize)
                self.csocket.send(send_msg.encode('utf-8'))
                l=f.read(BUFFER_SIZE)
                while fsize>0:
                    self.csocket.send(l)
                    fsize = fsize - BUFFER_SIZE
                    l=f.read(BUFFER_SIZE)
                    if fsize<=0:
                        f.close()
            except IOError:
                print('Unable to open the file\n')

            
            
            loop_no = loop_no-1


def main():
    server_Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_Socket.bind((Host,port))
    threads =[]

    while True:
        server_Socket.listen(6)
        client_soc,clientIp = server_Socket.accept()
        n_peer = peerThread(client_soc,clientIp)
        n_peer.start()
        threads.append(n_peer)
    
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()






		
		
		
		
		