import time
from datetime import datetime
import socket
import platform
import pickle

cook_var = 0  # golabal variable to assign cookies
BUFFER_SIZE = 2048


class Peer():
    def __init__(self, host, port, cookie=None):
        self.host = host
        if cookie != None:
            self.cookie = cookie
            self.active_no = self.active_no + 1
        else:
            self.cookie = cook_var + 1
            self.active_no = 0
        self.active_flag = True
        self.TTL = 7200
        self.port = port
        self.recent_Time = time.strftime("%H:%M:%S")


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


def isStatus(plist,
             host):  # checking whether my peer is active or not. Using it when peer who has registered with the server changes from inactive to active
    tmp = plist.head
    while tmp != None:
        p_obj = tmp.peer_obj
        if p_obj.host == host and p_obj.active_flag == True:
            return True
        tmp = tmp.next
    return False


def setStatus(plist, host,
              status):  # setting status to True if inactive user trying to become active and  False when active-> inactive i.e leave msg
    tmp = plist.head
    while tmp != None:
        p_obj = tmp.peer_obj
        if p_obj.host == host:
            p_obj.active_flag = status
            # should i change TTL value to 0 if it becomes inactive and 7200 when it becomes active
            break
        tmp = tmp.next


def getActive(plist):
    ret_list = Peerlist()
    tmp = plist.head
    while tmp != None:
        p_obj = tmp.peer_obj
        if p_obj.active_flag == True:
            ret_list.add(p_obj)
        tmp = tmp.next

    return ret_list


def set_TTL(plist, host):
    tmp = plist.head
    while tmp != None:
        p_obj = tmp.peer_obj
        if p_obj.host == host and p_obj.active_flag == True:
            p_obj.TTL = 7200
            break
        tmp = tmp.next
    return False


def getDetail(msg):
    li = msg.split("\n")
    ret_host = li[1]
    ret_host = ret_host[ret_host.index('Host') + 5:ret_host.index(' <cr>')]

    ret_port = li[2]
    ret_port = ret_port[ret_port.index('Port') + 5:ret_port.index(' <cr>')]

    ret_cookie = li[3]
    ret_cookie = ret_cookie[ret_cookie.index('Cookie') + 6:ret_cookie.index(' <cr>')]

    return ret_host, ret_port, ret_cookie


def main():
    PORT = 65500
    HOST = ''
    reg_peerlist = Peerlist()
    active_peerlist = Peerlist()

    socket_inp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_inp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    socket_inp.bind((HOST, PORT))
    socket_inp.listen(6)  # maximum number in wait queue
    print("RS server started")

    while True:
        con, address = socket_inp.accept()
        mf = 'utf-8'
        msg = con.recv(BUFFER_SIZE).decode(mf)

        host, port, cookie = getDetail(msg)
        print("Message from client:\n ", msg)

        if 'Register' in msg:
            p_obj = Peer(host, port, cookie)

            if isPresent(reg_peerlist, host):
                if isStatus(reg_peerlist, host) == False:
                    setStatus(reg_peerlist, host, True)
            else:
                reg_peerlist.add(p_obj)
                print("Sending back cookie info to the client")
                send_msg = 'POST peer-cookie ' + str(
                    p_obj.cookie) + ' <cr> <lf>\nFrom ' + socket.gethostname() + ' <cr> <lf>\nLast Message Sent: ' + str(
                    datetime.now()) + ' <cr> <lf>\nOperating System ' + str(platform.platform()) + ' <cr> <lf>\n'
                con.send(send_msg.encode(mf))
            con.close()
        # end of register message

        else:
            active_peerlist = getActive(reg_peerlist)

            if 'PQuery' in msg:
                so1 = socket.gethostbyname()
                so2 = str(datetime.now())
                so3 = str(platform.platform())
                if isPresent(active_peerlist, host):
                    active_peerlist.delete(host)  # sending all active peerlists without the host which requested
                    send_msg = 'POST PQuery Found<cr> <lf>\nFrom ' + so1 + ' <cr> <lf>\nLast Message Sent: ' + so2 + ' <cr> <lf>\nOperating System ' + so3
                    con.send(send_msg.encode(mf))
                    con.send(pickle.dumps(active_peerlist, pickle.HIGHEST_PROTOCOL))
                else:
                    send_msg = 'POST 404 ERROR <cr> <lf>\nFrom ' + so1 + ' <cr> <lf>\nLast Message Sent: ' + s02 + ' <cr> <lf>\nOperating System ' + so3
                    con.send(send_msg.encode(mf))
                    con.close()
            # end of pquery message

            elif 'Leave' in msg:

                if isPresent(active_peerlist, host):
                    setStatus(reg_peerlist, host, False)  # The active flag of the host is set to False
                    send_msg = 'POST Leave Successful<cr> <lf>\nFrom ' + socket.gethostname() + ' <cr> <lf>\nLast Message Sent: ' + str(
                        datetime.now()) + ' <cr> <lf>\nOperating System ' + str(platform.platform())
                    con.send(send_msg.encode(mf))
                con.close()


            elif 'KeepAlive' in msg:
                so1=socket.gethostbyname()
                so2=str(datetime.now())
                so3=str(platform.platform())
                if isPresent(active_peerlist, host):
                    set_TTL(reg_peerlist, host)
                    send_msg = 'POST Update TTL Successful<cr> <lf>\nFrom ' + so1 + ' <cr> <lf>\nLast Message Sent: ' + so2 + ' <cr> <lf>\nOperating System ' + so3
                else:
                    send_msg = 'POST 404 ERROR <cr> <lf>\nFrom ' + so1 + ' <cr> <lf>\nLast Message Sent: ' + so2 + ' <cr> <lf>\nOperating System ' + so3
                con.send(send_msg.encode(mf))
                con.close()


if __name__ == "__main__":
    main()
