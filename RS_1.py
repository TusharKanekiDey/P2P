import time
import threading
from datetime import datetime
import socket
import platform
import pickle
from threading import Thread
from socketserver import ThreadingMixIn


cook_var =0 # glabal variable to assign cookies
BUFFER_SIZE = 2048

def set_cook():
    global cook_var
    cook_var = cook_var +1
    return cook_var

class TTLThread(Thread):
    def __init__(self,ttl):
        Thread.__init__(self)
        self.TTL = ttl
    
    def run(self):
        while self.TTL:
            time.sleep(1)
            self.TTL = self.TTL -1
            print(self.TTL)


class Peer():

    def __init__(self,host,port,cookie=None):
        self.host = host
        if cookie!= 'None':
            self.cookie=cookie
            self.active_no = update_active(host,reg_peerlist)
        else:
            self.cookie = set_cook()
            self.active_no =1
        self.active_flag = True
        self.TTL = TTLThread(40)
        self.port = port
        self.recent_Time = time.strftime("%H:%M:%S")

class PeerNode():
    def __init__(self,peer):
        self.peer_obj = peer
        self.next = None

class Peerlist():
    def __init__(self):
        self.head = None
    
    def add(self,peer_obj):
        node = PeerNode(peer_obj)
        node.next=self.head
        self.head = node
    
    def delete(self,host):
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
            
    
def isPresent(plist,host):
    tmp = plist.head
    while(tmp != None):
        p_obj = tmp.peer_obj
        if p_obj.host == host:
            return True
        tmp = tmp.next
    return False

def isStatus(plist,host): #checking whether my peer is active or not. Using it when peer who has registered with the server changes from inactive to active
    tmp = plist.head
    while tmp!=None:
        p_obj = tmp.peer_obj
        if p_obj.host == host and p_obj.active_flag == True:
            return True
        tmp = tmp.next
    return False

def setStatus(plist,host,status): #setting status to True if inactive user trying to become active and  False when active-> inactive i.e leave msg
    tmp = plist.head
    while tmp!=None:
        p_obj = tmp.peer_obj
        if p_obj.host == host:
            p_obj.active_flag = status
            #should i change TTL value to 0 if it becomes inactive and 7200 when it becomes active
            break
        tmp = tmp.next

def getActive(plist):
    ret_list = Peerlist()
    tmp = plist.head
    while tmp!=None:
        p_obj = tmp.peer_obj
        if p_obj.active_flag == True:
            ret_list.add(p_obj)
        tmp = tmp.next
    
    return ret_list

def update_active(host,plist):
    tmp = plist.head
    while tmp!= None:
        p_obj = tmp.peer_obj
        if p_obj.host == host:
            p_obj.active_no = p_obj.active_no + 1
            break
        tmp = tmp.next

    
def set_TTL(plist,host):
    tmp = plist.head
    while tmp!=None:
        p_obj = tmp.peer_obj
        if p_obj.host == host and p_obj.active_flag == True:
            p_obj.TTL = 40
            break
        tmp = tmp.next
    return False

def getDetail(msg):
    li = msg.split("\n")
    ret_host = li[1]
    ret_host = ret_host[ret_host.index('Host')+5:ret_host.index(' <cr>')]

    ret_port = li[2]
    ret_port = ret_port[ret_port.index('Port')+5:ret_port.index(' <cr>')]

    ret_cookie = li[3]
    ret_cookie = ret_cookie[ret_cookie.index('Cookie')+6:ret_cookie.index(' <cr>')].strip()  

    #print("Get Detail :\n")
    #print(ret_host,ret_port,ret_cookie)
    return ret_host,ret_port,ret_cookie


reg_peerlist = Peerlist()


class RSThread(threading.Thread):
    def __init__(self,socket,clientIP):
        threading.Thread.__init__(self)
        self.lock=threading.Lock()
        #print(self.lock)
        self.csocket=socket
        self.ip=clientIP[0]
        self.socket=clientIP[1]
    
    def run(self):
        msg = self.csocket.recv(BUFFER_SIZE).decode('utf-8')
        active_peerlist = Peerlist()
        
        host,port,cookie = getDetail(msg)
        print("Message from client:\n ",msg)

        if 'Register' in msg:
            #if cookie == 'None':
                #p_obj = Peer(host,port)
            #else:
            p_obj = Peer(host,port,cookie)

            if isPresent(reg_peerlist,host) :
                setStatus(reg_peerlist,host,True)
                send_msg = 'POST Already exists cookie ' + str(p_obj.cookie) +' <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) +' <cr> <lf>\n'
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()
               
            else:
                reg_peerlist.add(p_obj)
                print("Sending back cookie info to the client")
                send_msg = 'POST peer-cookie ' + str(p_obj.cookie) +' <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform()) +' <cr> <lf>\n'
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()
        #end of register message

        elif 'PQuery' in msg:
            active_peerlist = getActive(reg_peerlist)

            if isPresent(active_peerlist,host):
                active_peerlist.delete(host) #sending all active peerlists without the host which requested
                send_msg = 'POST PQuery Found<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))

                active_no = 0
                tmp_o = active_peerlist.head
                data =''
                while tmp_o!= None:
                    tmp_obj = tmp_o.peer_obj
                    data += tmp_obj.host + ','+tmp_obj.port+'*'
                    tmp_o = tmp_o.next 
                print(data)
                self.csocket.sendall(data.encode('utf-8'))

                #self.lock.acquire()
                #self.csocket.send(pickle.dumps(active_peerlist,pickle.HIGHEST_PROTOCOL))
                #self.csocket.send(active_peerlist.encode('utf-8'))
                #self.lock.release()
            else:
                send_msg = 'POST 404 ERROR <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()
        #end of pquery message

        elif 'Leave' in msg:
            active_peerlist = getActive(reg_peerlist)
            if isPresent(active_peerlist,host):
                setStatus(reg_peerlist,host,False)  #The active flag of the host is set to False
                send_msg = 'POST Leave Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()
            else:
                self.csocket.close()
            
			
        
        elif 'KeepAlive' in msg:
            active_peerlist = getActive(reg_peerlist)
            if isPresent(active_peerlist,host):
                set_TTL(reg_peerlist,host)
                send_msg = 'POST Update TTL Successful<cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()
				
            else:
                send_msg = 'POST 404 ERROR <cr> <lf>\nFrom '+ socket.gethostname() +' <cr> <lf>\nLast Message Sent: '+str(datetime.now())+' <cr> <lf>\nOperating System ' + str(platform.platform())
                self.csocket.send(send_msg.encode('utf-8'))
                self.csocket.close()

def activeMain(plist):
    while True:
        time.sleep(3)
        active_plist = getActive(plist)
        tmp1 = active_plist.head
        if tmp1 !=None:
            while tmp1!=None:
                p_obj1 = tmp1.peer_obj
                if p_obj1.TTL == 0:
                    setStatus(reg_peerlist,p_obj1.host,False)
                tmp1 = tmp1.next



def main():
    PORT = 65500
    HOST = ''
    global reg_peerlist 
    #active_peerlist = Peerlist()
   
    socket_inp = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    socket_inp.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    socket_inp.bind((HOST,PORT))
    rs_threads =[]
     
    print("RS server started")
    ActiveThread = threading.Thread(target=activeMain,args=(reg_peerlist,))
    ActiveThread.start()

    while True:
        socket_inp.listen(6) # maximum number in wait queue
        con,address = socket_inp.accept()
        
        n_rs = RSThread(con,address)
        n_rs.start()
        rs_threads.append(n_rs)

    for thread in rs_threads:
        thread.join()

if __name__ == "__main__":
    main()


